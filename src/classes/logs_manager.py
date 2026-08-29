import os

import discord
from discord.ext import commands
from discord.ext.commands import hybrid_group

import dotenv
from dotenv import load_dotenv

from src.utils.helper import check_perms

load_dotenv()

class LogsManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = None
        if os.getenv("LOGS_CHANNEL_ID"):
            self.channel_id = int(os.getenv("LOGS_CHANNEL_ID"))
        self.role_id = None
        if os.getenv("LOGS_ROLE_ID"):
            self.role_id = int(os.getenv("LOGS_ROLE_ID"))

    @hybrid_group()
    async def logs(self, ctx):
        pass

    @logs.command(
        description="Check the current configuration for honeypot logs."
    )
    @check_perms()
    async def info(self, ctx):
        if not self.channel_id:
            await ctx.send("Logs haven't been configured yet! Run `/logs setup` first.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Honeypot Logs Configuration",
            description=f"**Channel**: {ctx.guild.get_channel(self.channel_id).jump_url}"
                        f"\n**Ping Role**: {ctx.guild.get_role(self.role_id).mention}",
            color=0xd8a31e
        )

        await ctx.send(embed=embed)

    @logs.command(
        description="Configure honeypot logs."
    )
    @check_perms()
    async def setup(self, ctx, channel: discord.TextChannel, ping_role: discord.Role):
        dotenv.set_key(".env", "LOGS_CHANNEL_ID", str(channel.id))
        self.channel_id = int(channel.id)
        dotenv.set_key(".env", "LOGS_ROLE_ID", str(ping_role.id))
        self.role_id = int(ping_role.id)

        embed = discord.Embed(
            title="Honeypot Logs Configuration",
            description=f"**Channel**: {ctx.guild.get_channel(self.channel_id).jump_url}"
                        f"\n**Ping Role**: {ctx.guild.get_role(self.role_id).mention}",
            color=0xd8a31e
        )

        await ctx.send(embed=embed)

    async def log(self, message, action, duration):
        guild = message.guild

        duration_msg = ""

        if not duration == "N/A":
            duration_msg = f"**Duration:** {duration}h"

        embed = discord.Embed(
            title="Honeypot Log",
            description=f"**Channel**: {message.guild.get_channel(self.channel_id).jump_url}\n"
                        f"**User**: {message.author.mention}\n"
                        f"**Action Taken**: {action}\n"
                        f"{duration_msg}",
            color=0xd8a31e
        )

        await guild.get_channel(self.channel_id).send(guild.get_role(self.role_id).mention, embed=embed)


async def setup(bot):
    await bot.add_cog(LogsManager(bot))