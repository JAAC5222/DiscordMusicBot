import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import yt_dlp
import asyncio
from cachetools import TTLCache

# Variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configuración y permisos
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix = 'q.', intents=intents)

# Cola de reproducción y caché
songQueue = []
searchCache = TTLCache(maxsize=100, ttl=300)

# Comandos y eventos
@bot.event
async def on_ready():
    print(f'{bot.user.name} conectado!')

@bot.event
async def on_message(message):
    print(f'Mensaje recibido: {message.content}')
    await bot.process_commands(message)

@bot.command(name = 'join', help='Conecta al bot al canal de voz')
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send('No estás conectado a un canal de voz')
        return
    channel = ctx.author.voice.channel
    await channel.connect()

@bot.command(name = 'leave', help='Desconecta al bot del canal de voz')
async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.send("No estoy conectado a ningún canal de voz.")
    else:
        await ctx.voice_client.disconnect()
        await ctx.send("Me he desconectado del canal de voz.")

@bot.command(name ='play', help='Reproduce una canción de YouTube')
async def play(ctx, *, search: str):
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("No estás conectado a un canal de voz, y yo tampoco.")
            return

    voice_client = ctx.voice_client

    # Verificar caché
    if search in searchCache:
        song = searchCache[search]
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True
        }

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(f"ytsearch:{search}", download=False))

        if 'entries' not in data or len(data['entries']) == 0:
            await ctx.send("No se pudo encontrar la canción.")
            return

        info = data['entries'][0]
        url = info['url']
        title = info['title']

        song = {'url': url, 'title': title}
        searchCache[search] = song

    songQueue.append(song)
    await ctx.send(f'Añadido a la cola: **{song["title"]}**')

    if not voice_client.is_playing():
        await play_next(ctx)

async def play_next(ctx):
    if len(songQueue) > 0:
        song = songQueue.pop(0)
        url = song['url']
        title = song['title']
        voice_client = ctx.voice_client
        source = await discord.FFmpegOpusAudio.from_probe(url, method='fallback')

        def after_playing(error):
            if len(songQueue) > 0:
                ctx.bot.loop.create_task(play_next(ctx))
            else:
                ctx.bot.loop.create_task(ctx.send("La cola ha terminado."))

        voice_client.play(source, after=after_playing)
        await ctx.send(f'Reproduciendo: **{title}**')

@bot.command(name = 'queue', help='Muestra la cola de canciones')
async def queue(ctx):
    if len(songQueue) == 0:
        await ctx.send("La cola está vacía.")
    else:
        queue_str = '\n'.join([f"{i+1}. {song['title']}" for i, song in enumerate(songQueue)])
        await ctx.send(f"Cola de reproducción:\n{queue_str}")

# Iniciar bot
bot.run(TOKEN)
