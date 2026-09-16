import json
import logging
import os
from collections import defaultdict
from datetime import timedelta, datetime
from pathlib import Path

import discord
from discord.ext import commands

from src.classes.database_manager import DatabaseManager
from src.classes.logs_manager import LogsManager

logger = logging.getLogger("discord")

class MessageManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()
        self.message_cache = defaultdict(list)
        self.CACHE_TTL = timedelta(seconds=10)
        self.log_manager = LogsManager(self.bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        now = datetime.now()
        user_id = message.author.id

        self.message_cache[user_id] = [
            (msg, ts) for msg, ts in self.message_cache[user_id]
            if now - ts < self.CACHE_TTL
        ]
        self.message_cache[user_id].append((message, now))

        honeypot_list = self.db.get_channels(message.guild.id)
        honeypot = {}

        for h in honeypot_list:
            if message.channel.id == h[2]:
                honeypot = h
                break

        if not honeypot:
            return

        try:
            reason_msg = f"# You triggered a honeypot in ***{message.guild.name}!***\n\n**Action taken:** "
            footer = "\n-# Please contact a moderator if this was a mistake."

            match honeypot[3]:
                case "mute":
                    await message.author.timeout(
                        timedelta(hours=honeypot[4]),
                        reason=reason_msg
                        )
                    await message.author.send(reason_msg + honeypot[3] + footer)
                case "kick":
                    await message.author.send(reason_msg + honeypot[3] + footer)
                    await message.author.kick(reason=reason_msg)

                    honeypot[4] = "N/A"
                case "ban":
                    await message.author.send(reason_msg + honeypot[3] + footer)
                    await message.author.ban(reason=reason_msg)

                    honeypot[4] = "N/A"
                case _:
                    pass

            cached_entries = self.message_cache.pop(user_id, [])
            for cached_msg in cached_entries:
                try:
                    await cached_msg[0].delete()
                except discord.Forbidden:
                    pass
                except discord.NotFound:
                    pass
            await self.log_manager.log(message, honeypot[3], honeypot[4])
        except discord.Forbidden:
            logger.error(f"Lacking permissions to moderate user {user_id}")

async def setup(bot):
    await bot.add_cog(MessageManager(bot))