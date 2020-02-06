import random
import discord
from discord.ext import commands


class utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'{round(self.bot.latency*1000)}ms')

    @commands.command(aliases=['coin', 'flip', 'flip a coin'])
    async def coinflip(self, ctx):
        """Flip a coin."""
        await ctx.send(random.choice(['Heads', 'Tails']))


def setup(bot):
    bot.add_cog(utility(bot))
