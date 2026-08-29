import json
import logging
import os
from collections import defaultdict
from datetime import timedelta, datetime
from pathlib import Path

import discord
from discord.ext import commands

logger = logging.getLogger("discord")

class MessageManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = defaultdict(list)
        self.CACHE_TTL = timedelta(seconds=10)
        self.honeypot_list = []
        self.get_honeypots()

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
            else:
                return

        try:
            await message.author.timeout(
                timedelta(hours=honeypot["duration"]),
                reason=f"Honeypot triggered: sent a message in {message.guild.get_channel(honeypot['channel']).jump_url}"
                )

            cached_entries = self.message_cache.pop(user_id, [])
            for cached_msg in cached_entries:
                try:
                    await cached_msg[0].delete()
                except discord.Forbidden:
                    pass
                except discord.NotFound:
                    pass
        except discord.Forbidden:
            logger.error(f"Lacking permissions to moderate user {user_id}")

async def setup(bot):
    await bot.add_cog(MessageManager(bot))