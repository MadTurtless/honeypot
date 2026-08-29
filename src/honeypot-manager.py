import logging

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger("discord")

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

    @commands.hybrid_group("honeypot")
    async def honeypot(self, ctx):
        return

    @honeypot.command(
        description="Add a honeypot to your server."
    )
    @app_commands.choices(
        punishment_type=[
            app_commands.Choice(name="Ban", value="Ban"),
            app_commands.Choice(name="Kick", value="Kick"),
            app_commands.Choice(name="Mute", value="Mute"),
        ]
    )
    @app_commands.describe(
        channel="The channel you'd like to turn into a honeypot.",
        punishment_type="What you want the bot to do when the hp gets triggered.",
        punishment_duration="How you want the honeypot to last in hours (default: 168h, 7d)."
    )
    async def create(self, ctx, channel: discord.TextChannel, punishment_type: app_commands.Choice[str], punishment_duration: int=168):
        await ctx.send("Creating a honeypot...")

async def setup(bot):
    await bot.add_cog(Commands(bot))