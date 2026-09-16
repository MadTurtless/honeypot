import json
from json import JSONDecodeError

from discord.ext import commands

from src.classes.database_manager import DatabaseManager

db = DatabaseManager()

def check_perms():
    async def predicate(ctx):
        if ctx.author == ctx.guild.owner:
            return True

        if ctx.author.guild_permissions.administrator:
            return True

        permitted_role_id = db.get_perms(ctx.guild.id)[1]

        for role in ctx.author.roles:
            if role.id == permitted_role_id:
                return True

        await ctx.send("You don't have enough permissions to run this command.", ephemeral=True)
        return False
    return commands.check(predicate)