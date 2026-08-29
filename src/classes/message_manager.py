import json
import logging
import os
from collections import defaultdict
from datetime import timedelta, datetime
from pathlib import Path

import discord
from discord.ext import commands

from src.classes.logs_manager import LogsManager

logger = logging.getLogger("discord")

class MessageManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = defaultdict(list)
        self.CACHE_TTL = timedelta(seconds=10)
        self.honeypot_list = []
        self.get_honeypots()
        self.log_manager = LogsManager(self.bot)

    def get_honeypots(self):
        h_list = []
        for h in os.listdir(Path("src/honeypot-settings")):
            h_list.append(json.load(open(Path(f"src/honeypot-settings/{h}"))))

        self.honeypot_list = h_list

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

        honeypot = {}

        for h in self.honeypot_list:
            if message.channel.id == h["channel"]:
                honeypot = h
                break

        if not honeypot:
            return

        try:
            reason_msg = f"# You triggered a honeypot in ***{message.guild.name}!***\n\n**Action taken:** "
            footer = "\n-# Please contact a moderator if this was a mistake."

            match honeypot["type"]:
                case "mute":
                    await message.author.timeout(
                        timedelta(hours=honeypot["duration"]),
                        reason=reason_msg
                        )
                    await message.author.send(reason_msg + honeypot["type"] + footer)
                case "kick":
                    await message.author.send(reason_msg + honeypot["type"] + footer)
                    await message.author.kick(reason=reason_msg)

                    honeypot["duration"] = "N/A"
                case "ban":
                    await message.author.send(reason_msg + honeypot["type"] + footer)
                    await message.author.ban(reason=reason_msg)

                    honeypot["duration"] = "N/A"
                case _:
                    pass

            cached_entries = self.message_cache.pop(user_id, [])
            for cached_msg in cached_entries:
                try:
                    await cached_msg[0].delete()
                    await self.log_manager.log(message, honeypot["type"], honeypot["duration"])
                except discord.Forbidden:
                    pass
                except discord.NotFound:
                    pass
        except discord.Forbidden:
            logger.error(f"Lacking permissions to moderate user {user_id}")

async def setup(bot):
    await bot.add_cog(MessageManager(bot))