#Author JAAC/Asthok

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import yt_dlp

# Variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configuración y permisos
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix = 'q.', intents=intents)

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

@bot.command(name='play', help='Reproduce una canción de YouTube')
async def play(ctx, *, search: str):
    # Verificar si el bot está en un canal de voz
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("No estás conectado a un canal de voz, y yo tampoco.")
            return

    voice_client = ctx.voice_client

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
        except Exception as e:
            await ctx.send("No se pudo encontrar la canción.")
            return

        url = info['url']
        title = info['title']

        if not voice_client.is_playing():
            source = await discord.FFmpegOpusAudio.from_probe(url, method='fallback')
            voice_client.play(source)
            await ctx.send(f'Reproduciendo: **{title}**')
        else:
            await ctx.send('Ya estoy reproduciendo una canción.')


# Iniciar bot
bot.run(TOKEN)