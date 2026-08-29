import asyncio
import os
import logging
import sys

import discord
from discord.ext import commands

from dotenv import load_dotenv

old_factory = logging.getLogRecordFactory()

def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)

    if record.levelno >= logging.ERROR:
        record.file_info = f" - ({record.filename}:{record.lineno})"
    else:
        record.file_info = ""

    return record

logging.setLogRecordFactory(record_factory)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s]%(file_info)s - %(message)s",
    handlers=[
        logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a+"),
        logging.StreamHandler(stream=sys.stdout)
    ]
)

logger = logging.getLogger("discord")

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix="!")

@bot.event
async def on_ready():
    """
    This function is called when the bot is online.
    It attempts to synchronise all commands
    :return:
    """
    logger.info(f"{bot.user} has connected to Discord!")

    try:
        synced = await bot.tree.sync()
        logger.info(f"{bot.user} has synced {len(synced)} commands")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

async def main():
    """
    This is the entry point for the bot.
    It makes sure to add all cogs and then starts it.
    :return:
    """
    extensions = {"src.honeypot_manager"}

    async with bot:
        for e in extensions:
            await bot.load_extension(e)
        await bot.start(token)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    logger.info("Shutting down...\n"
                "================================================================\n")
