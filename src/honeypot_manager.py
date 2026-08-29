import json
import logging
import os
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from src.embed_gui_manager import EmbedGui

logger = logging.getLogger("discord")

def update_or_create_hp(channel: discord.TextChannel, punishment_type: app_commands.Choice[str],
        punishment_duration: int = 168):

    settings = {
        "channel": int(channel.id),
        "type": punishment_type.value,
        "duration": punishment_duration
    }

    with open(Path(f"src/honeypot-settings/{channel.id}.json"), "w") as f:
        json.dump(settings, f, indent=4)
    f.close()

    embed = discord.Embed(
        title="Honeypot Created",
        description=f"**Channel:** {channel.jump_url}"
                    f"\n**Punishment:** {punishment_type.name}"
                    f"\n**Duration:** {punishment_duration} hours",
        color=0xd8a31e
    )

    return embed

class HoneypotManager(commands.Cog):
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
        if os.path.isfile(f"src/honeypot-settings/{channel.id}.json"):
            await ctx.send("A honeypot for this channel already exists!", ephemeral=True)
            return

        embed = update_or_create_hp(channel, punishment_type, punishment_duration)

        await ctx.send(embed=embed)

    @honeypot.command(
        description="Edit an existing honeypot."
    )
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
        embed = update_or_create_hp(channel, punishment_type, punishment_duration)

        await ctx.send(embed=embed)

    @honeypot.command(
        description="Remove a honeypot from your server.",
    )
    @app_commands.describe(
        channel="The channel you'd like to remove the honeypot from.",
    )
    async def remove(self, ctx, channel: discord.TextChannel):
        if not os.path.exists(Path(f"src/honeypot-settings/{channel.id}.json")):
            await ctx.send("Channel isn't a honeypot!", ephemeral=True)
            return

        os.remove(Path(f"src/honeypot-settings/{channel.id}.json"))
        await ctx.send(f"Removed honeypot from #{channel.jump_url}")

    @honeypot.command(
        description="Get the channel's honeypot settings."
    )
    @app_commands.describe(
        channel="The channel you'd like to get the honeypot from.",
    )
    async def info(self, ctx, channel: discord.TextChannel):
        if not os.path.exists(Path(f"src/honeypot-settings/{channel.id}.json")):
            await ctx.send("Channel is not a honeypot!", ephemeral=True)
            return

        settings = json.load(open(Path(f"src/honeypot-settings/{channel.id}.json")))
        embed = discord.Embed(
            title="Honeypot Created",
            description=f"**Channel:** {channel.jump_url}"
                            f"\n**Punishment:** {settings.punishment_type.name}"
                            f"\n**Duration:** {settings.punishment_duration} hours",
            color=0xd8a31e
        )

        await ctx.send(embed=embed)

    @honeypot.command(
        description="Get a list of all honeypots."
    )
    async def list(self, ctx):
        honeypots = []

        for h in os.listdir(Path("src/honeypot-settings/")):
            honeypots.append(json.load(open(Path(f"src/honeypot-settings/{h}"), "r")))

        view = EmbedGui(honeypots, ctx)
        await ctx.send(embed=view.create_embed(), view=view)

async def setup(bot):
    await bot.add_cog(HoneypotManager(bot))