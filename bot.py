#Author JAAC/Asthok

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

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

@bot.command(name='join', help='Conecta al bot al canal de voz')
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send('No estás conectado a un canal de voz')
        return
    channel = ctx.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='Desconecta al bot del canal de voz')
async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.send("No estoy conectado a ningún canal de voz.")
    else:
        await ctx.voice_client.disconnect()
        await ctx.send("Me he desconectado del canal de voz.")

# Iniciar bot
bot.run(TOKEN)