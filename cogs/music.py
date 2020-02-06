import discord
from discord.ext import commands
import youtube_dl
import asyncio
import random

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': './yt/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address':
    '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {'options': '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options),
                   data=data)


def get_voice_client(bot):
    if bot.voice_clients:
        return bot.voice_clients[0]
    return None


class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        for chan in self.bot.get_all_channels():
            if isinstance(chan, discord.VoiceChannel):
                self.target_channel = chan
                break

        for chan in self.bot.get_all_channels():
            if isinstance(chan, discord.TextChannel) and chan.name.lower() == 'general':
                self.general_text_channel = chan
                break

        self.bot.bg_task = self.bot.loop.create_task(self.task())
        self.play_sem = asyncio.Semaphore(0)
        print('Music Cog Init')

    async def task(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await self.play_sem.acquire()
            # await self.general_text_channel.send('Checking Queue...')
            if not self.queue:
                await self.general_text_channel.send('Queue Empty!')
                if get_voice_client(self.bot):
                    await get_voice_client(self.bot).disconnect()
                continue
            url = self.queue[0]
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            player.volume = 0.1
            if not get_voice_client(self.bot):
                await self.join()
            get_voice_client(self.bot).play(player,
                                            after=self.player_done)
            await self.general_text_channel.send('Now playing: {}'.format(player.title))

    def player_done(self, e):
        if e:
            print('Player error: %s' % e)
        self.queue.pop(0)
        self.play_sem.release()

    @commands.command(hidden=True)
    async def set_target_channel(self, ctx, channel: discord.VoiceChannel):
        self.target_channel = channel

    @commands.command()
    async def add(self, ctx, url: str):
        self.queue.append(url)

    @commands.command()
    async def pop(self, ctx):
        if self.queue:
            await ctx.send(f'Removed {self.queue.pop(0)}')

    @commands.command()
    async def clear(self, ctx):
        self.queue.clear()

    @commands.command()
    async def queue(self, ctx):
        if self.queue:
            await ctx.send('\n'.join(self.queue))
        else:
            await ctx.send('Queue Empty!')

    @commands.command()
    async def shuffle(self, ctx):
        random.shuffle(self.queue)

    @commands.command()
    async def play(self, ctx):
        if not ctx.voice_client:
            await self.join(ctx)
        self.play_sem.release()

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        # TODO(justin): pause music?
        await self.leave(ctx)

    @commands.command(hidden=True)
    async def join(self, ctx):
        """Joins the target channel."""
        if ctx.voice_client:
            await ctx.voice_client.move_to(self.target_channel)
            return
        await self.target_channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    @commands.command()
    async def volume(self, ctx, volume: int = None):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        if volume is None:
            return await ctx.send(f'Volume is currently {round(ctx.voice_client.source.volume*100)}%')

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    # @play.before_invoke
    # async def ensure_voice(self, ctx):
    #     if ctx.voice_client is None:
    #         if ctx.author.voice:
    #             await ctx.author.voice.channel.connect()
    #         else:
    #             await ctx.send("You are not connected to a voice channel.")
    #             raise commands.CommandError(
    #                 "Author not connected to a voice channel.")
    #     elif ctx.voice_client.is_playing():
    #         ctx.voice_client.stop()


def setup(bot):
    bot.add_cog(music(bot))


def teardown(bot):
    bot.bg_task.cancel()
