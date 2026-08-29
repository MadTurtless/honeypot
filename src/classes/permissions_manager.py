import json
from json import JSONDecodeError
from pathlib import Path

import discord
from discord.ext import commands
from discord.ext.commands import hybrid_group

from src.utils.helper import check_perms


class PermissionsManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_path = "src/utils/permitted_roles.json"

    @hybrid_group()
    async def perms(self, ctx):
        pass

    @perms.command(
        description="Add a role to the list of roles that can run Honeypot commands.",
    )
    @check_perms()
    async def add(self, ctx, role: discord.Role):
        try:
            roles = json.load(open(self.roles_path))
            roles.append(role.id)
        except JSONDecodeError:
            roles = [role.id]

        json.dump(roles, open(self.roles_path, "w"), indent=4)

        await ctx.send(f"Successfully added {role.name} to permitted roles.", ephemeral=True)

    @perms.command(
        description="Remove a role from the list of roles that can run Honeypot commands.",
    )
    @check_perms()
    async def remove(self, ctx, role: discord.Role):
        try:
            roles = json.load(open(self.roles_path))
            roles.remove(role.id)
        except JSONDecodeError:
            roles = [role.id]

        json.dump(roles, open(self.roles_path, "w"), indent=4)

        await ctx.send(f"Successfully removed {role.name} from permitted roles.", ephemeral=True)

    @perms.command(
        description="View the list of roles that can run Honeypot commands.",
    )
    @check_perms()
    async def list(self, ctx):
        try:
            roles = json.load(open("src/utils/permitted_roles.json"))
        except JSONDecodeError:
            roles = []

        embed = discord.Embed(
            title="Permitted Roles List",
        )

        for i  in range(len(roles)):
            embed.add_field(name="", value=f"{i + 1}: {ctx.guild.get_role(roles[i]).mention}", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PermissionsManager(bot))