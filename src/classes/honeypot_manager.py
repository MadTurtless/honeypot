import json
import logging
import os
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from src.classes.database_manager import DatabaseManager
from src.utils.embed_gui_manager import EmbedGui
from src.utils.helper import check_perms

logger = logging.getLogger("discord")

class HoneypotManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()

    @commands.hybrid_group()
    async def honeypot(self, ctx):
        return

    @honeypot.command(
        description="Add a honeypot to your server."
    )
    @check_perms()
    @app_commands.choices(
        punishment_type=[
            app_commands.Choice(name="Mute", value="mute"),
            app_commands.Choice(name="Kick", value="kick"),
            app_commands.Choice(name="Ban", value="ban")
        ]
    )
    @app_commands.describe(
        channel="The channel you'd like to turn into a honeypot.",
        punishment_type="What you want the bot to do when the hp gets triggered. (Mute is recommended)",
        punishment_duration="How you want the honeypot to last in hours (default: 168h, 7d)."
    )
    async def create(self, ctx, channel: discord.TextChannel, punishment_type: app_commands.Choice[str], punishment_duration: int=168):
        if not self.db.get_channels(ctx.guild.id) == []:
            await ctx.send("A honeypot for this channel already exists!", ephemeral=True)
            return

        self.db.add_channel(ctx.guild.id, channel.id, punishment_type.value, punishment_duration)

        embed = discord.Embed(
            title="Honeypot Created",
            description=f"**Channel:** {channel.jump_url}"
                        f"\n**Punishment:** {punishment_type.value}"
                        f"\n**Duration:** {punishment_duration} hours",
            color=0xd8a31e
        )

        await ctx.send(embed=embed)

    @honeypot.command(
        description="Edit an existing honeypot."
    )
    @check_perms()
    @app_commands.choices(
        punishment_type=[
            app_commands.Choice(name="Mute", value="mute"),
            app_commands.Choice(name="Kick", value="kick"),
            app_commands.Choice(name="Ban", value="ban")
        ]
    )
    @app_commands.describe(
        channel="The channel you'd like to turn into a honeypot.",
        punishment_type="What you want the bot to do when the hp gets triggered. (Mute is recommended)",
        punishment_duration="How you want the honeypot to last in hours (default: 168h, 7d)."
    )
    async def edit(self, ctx, channel: discord.TextChannel, punishment_type: app_commands.Choice[str], punishment_duration: int=168):
        self.db.edit_channel(ctx.guild.id, channel.id, punishment_type.value, punishment_duration)

        embed = discord.Embed(
            title="Honeypot Created",
            description=f"**Channel:** {channel.jump_url}"
                        f"\n**Punishment:** {punishment_type.value}"
                        f"\n**Duration:** {punishment_duration} hours",
            color=0xd8a31e
        )

        await ctx.send(embed=embed)

    @honeypot.command(
        description="Remove a honeypot from your server.",
    )
    @check_perms()
    @app_commands.describe(
        channel="The channel you'd like to remove the honeypot from.",
    )
    async def remove(self, ctx, channel: discord.TextChannel):
        if not self.db.get_channels(ctx.guild.id):
            await ctx.send("Channel isn't a honeypot!", ephemeral=True)
            return

        self.db.remove_channel(ctx.guild.id, channel.id)
        await ctx.send(f"Removed honeypot from {channel.jump_url}")

    @honeypot.command(
        description="Get the channel's honeypot settings."
    )
    @check_perms()
    @app_commands.describe(
        channel="The channel you'd like to get the honeypot from.",
    )
    async def info(self, ctx, channel: discord.TextChannel):
        if not self.db.get_channels(ctx.guild.id):
            await ctx.send("Channel isn't a honeypot!", ephemeral=True)
            return

        settings = self.db.get_channel(ctx.guild.id, channel.id)
        print(settings)

        embed = discord.Embed(
            title="Honeypot Info",
            description=f"**Channel:** {channel.jump_url}"
                            f"\n**Punishment:** {settings[3]}"
                            f"\n**Duration:** {settings[4]}h",
            color=0xd8a31e
        )

        await ctx.send(embed=embed)

    @honeypot.command(
        description="Get a list of all honeypots."
    )
    @check_perms()
    async def list(self, ctx):
        honeypots = self.db.get_channels(ctx.guild.id)

        view = EmbedGui(honeypots, ctx)
        await ctx.send(embed=view.create_embed(), view=view)

async def setup(bot):
    await bot.add_cog(HoneypotManager(bot))