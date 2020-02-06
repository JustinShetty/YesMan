#!/usr/bin/env python3

import os
import config
import discord
from discord.ext import commands

description = 'Yes Man, at your service!'
bot = commands.Bot(command_prefix=commands.when_mentioned_or(""),
                   description=description,
                   case_insensitive=True)


@bot.event
async def on_ready():
    print('Bot Ready.')
    for chan in bot.get_all_channels():
        if isinstance(chan,
                      discord.TextChannel) and chan.name.lower() == 'general':
            await chan.send("At your service!")
            break
    _load()


def _load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')


@bot.command()
async def reload(ctx):
    """Reload extensions."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.reload_extension(f'cogs.{filename[:-3]}')


if __name__ == '__main__':
    bot.run(config.DISCORD_TOKEN)
