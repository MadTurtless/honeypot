import json
from json import JSONDecodeError

from discord.ext import commands

try:
    permitted_roles = json.load(open("src/utils/permitted_roles.json"))
except JSONDecodeError:
    roles = []

def check_perms():
    async def predicate(ctx):
        if ctx.author == ctx.guild.owner:
            return True

        if ctx.author.guild_permissions.administrator:
            return True

        for role in ctx.author.roles:
            if role.id in permitted_roles:
                return True

        await ctx.send("You don't have enough permissions to run this command.", ephemeral=True)
        return False
    return commands.check(predicate)