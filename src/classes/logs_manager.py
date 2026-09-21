import os

import discord
from discord.ext import commands
from discord.ext.commands import hybrid_group

import dotenv
from dotenv import load_dotenv

from src.classes.database_manager import DatabaseManager
from src.utils.helper import check_perms

load_dotenv()

class LogsManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()

    @hybrid_group()
    async def logs(self, ctx):
        pass

    @logs.command(
        description="Check the current configuration for honeypot logs."
    )
    @check_perms()
    async def info(self, ctx):
        channel_id = self.db.get_logs(ctx.guild.id)[1]
        if not channel_id:
            await ctx.send("Logs haven't been configured yet! Run `/logs setup` first.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Honeypot Logs Configuration",
            description=f"**Channel**: {ctx.guild.get_channel(channel_id).jump_url}"
                        f"\n**Ping Role**: {ctx.guild.get_role(role_id).mention}",
            color=0xd8a31e
        )

        await ctx.send(embed=embed)

    @logs.command(
        description="Configure honeypot logs."
    )
    @check_perms()
    async def setup(self, ctx, channel: discord.TextChannel, ping_role: discord.Role):
        self.db.configure_logs(ctx.guild.id, channel.id, ping_role.id)

        embed = discord.Embed(
            title="Honeypot Logs Configuration",
            description=f"**Channel**: {channel.jump_url}"
                        f"\n**Ping Role**: {ping_role.mention}",
            color=0xd8a31e
        )

        await ctx.send(embed=embed)

    async def log(self, message, action, duration):
        guild = message.guild
        channel_id = self.db.get_logs(guild.id)[1]
        role_id = self.db.get_logs(guild.id)[2]

        duration_msg = ""

        if not duration == "N/A":
            duration_msg = f"**Duration:** {duration}h"

        embed = discord.Embed(
            title="Honeypot Log",
            description=f"**Channel**: {message.jump_url}\n"
                        f"**User**: {message.author.mention}\n"
                        f"**Action Taken**: {action}\n"
                        f"{duration_msg}",
            color=0xd8a31e
        )

        await guild.get_channel(channel_id).send(guild.get_role(role_id).mention, embed=embed)


async def setup(bot):
    await bot.add_cog(LogsManager(bot))