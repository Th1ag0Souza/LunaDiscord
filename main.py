import yt_dlp
import discord
from discord.ext import commands
import asyncio
import os
import config

contador = 0

TOKEN = config.token

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}


class MusicBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []

    @commands.command()
    async def play(self, ctx, *, search):
        try:
            voice_channel = ctx.author.voice.channel if ctx.author.voice else None
            if not voice_channel:
                return await ctx.send("Você precisa entrar em uma call bobaum.")
            if ctx.voice_client is None:
                print("connected to voice channel")
                await voice_channel.connect()

            async with ctx.typing():
                print("preparing to add to queue")
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{search}", download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    url = info['url']
                    title = info['title']
                    self.queue.append((url, title))
                    await ctx.send(f'Adicionado a fila: **{title}**')
                    print("Adicionado a fila!")
            if not ctx.voice_client.is_playing():
                await self.play_next(ctx)
                print("Tocando a próxima.")

        except Exception as e:
            print(f"An error occurred: {e}")
            await ctx.send(
                f"An error occurred: {e}")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send(f"Tchau e Bença.")

    async def play_next(self, ctx):
        try:
            if self.queue:
                url, title = self.queue.pop()
                source = await discord.FFmpegOpusAudio.from_probe(url,
                **FFMPEG_OPTIONS)
                ctx.voice_client.play(source, after=lambda _: self.client.loop.create_task(self.play_next(ctx)))
                await ctx.send(f'Tocando agora: **{title}**')
            elif not ctx.voice_client.is_playing():
                await ctx.send("A fila esta vazia.")
        except Exception as e:
            print(f"An error occurred: {e}")
            await ctx.send(
                f"An error occurred: {e}")


    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Música pulada.")


client = commands.Bot(command_prefix='!', intents=intents)




@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")

async def main():
    await client.add_cog(MusicBot(client))
    await client.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())