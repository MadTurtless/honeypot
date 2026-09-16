import json
from json import JSONDecodeError
from pathlib import Path

import discord
from discord.ext import commands
from discord.ext.commands import hybrid_group

from src.classes.database_manager import DatabaseManager
from src.utils.helper import check_perms


class PermissionsManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()

    @hybrid_group()
    async def perms(self, ctx):
        pass

    @perms.command(
        description="Add a role to the list of roles that can run Honeypot commands.",
    )
    @check_perms()
    async def setup(self, ctx, role: discord.Role):
        self.db.configure_perms(ctx.guild.id, role.id)

        await ctx.send(f"Successfully added {role.mention} to permitted roles.", ephemeral=True)

    @perms.command(
        description="View the list of roles that can run Honeypot commands.",
    )
    @check_perms()
    async def info(self, ctx):
        role = self.db.get_perms(ctx.guild.id)

        if role is None:
            await ctx.send("No role was added to honeypot permissions. Please run `/perms setup` first!", ephemeral=True)
            return

        await ctx.send(f"Permission role: {ctx.guild.get_role(role[1]).mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PermissionsManager(bot))