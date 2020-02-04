#!/usr/bin/env python3

import os
import config
import discord
from discord.ext import commands

description = 'Yes Man, at your service!'
client = commands.Bot(command_prefix=commands.when_mentioned_or(";"),
                      description=description,
                      case_insensitive=True)


@client.event
async def on_ready():
    print('Bot Ready.')
    for chan in client.get_all_channels():
        if isinstance(chan,
                      discord.TextChannel) and chan.name.lower() == 'general':
            await chan.send("At your service!")
            break
    _reload()


@client.command()
async def reload(ctx):
    """Reload extensions."""
    _reload()


def _reload():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                client.unload_extension(f'cogs.{filename[:-3]}')
            except commands.ExtensionNotLoaded:
                pass
            client.load_extension(f'cogs.{filename[:-3]}')


if __name__ == '__main__':
    client.run(config.DISCORD_TOKEN)
