import random
from pprint import pprint
import discord
from discord.ext import commands


class utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'{round(self.client.latency*1000)}ms')

    @commands.command(aliases=['coin', 'flip', 'flip a coin'])
    async def coinflip(self, ctx):
        """Flip a coin."""
        await ctx.send(random.choice(['Heads', 'Tails']))

    @commands.command()
    async def info(self, ctx):
        """Placeholder so I can print stuff."""
        pprint(self.client.cogs)


def setup(client):
    client.add_cog(utility(client))
