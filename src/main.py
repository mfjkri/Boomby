#import libraries
import discord
import os
import time
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from keep_alive import keep_alive 

intents = discord.Intents.default()
intents.members = True

queues = {}
def check_queue(ctx, id):
  if queues[id] !={}:
    voice = ctx.guild.voice_client
    source = queues[id].pop(0)
    voice.play(source, after=lambda x=0: check_queue(ctx, ctx.message.guild.id))

client = commands.Bot(command_prefix = '!', intents=intents, help_command=None)

@client.event
async def on_ready():
  activity = discord.Game(name='Boomby')
  await client.change_presence(status=discord.Status.online, activity=activity)
  print('Logged in as {0.user}'.format(client))
  print('-------------------')





@client.command(pass_context = True)
async def help(ctx):
  embed = discord.Embed(colour = discord.Colour.magenta())
  embed.set_author(name='Command prefix: !')
  embed.add_field(name='help', value='Show available commands', inline=False)
  embed.add_field(name='join', value='Adds Boomby to your voice-channel', inline=False)
  embed.add_field(name='leave', value='Removes Boomby from your voice-channel', inline=False)    
  embed.add_field(name='play', value='Play song from youtube url or song name', inline=False)
  embed.add_field(name='pause', value='Pause song', inline=False)
  embed.add_field(name='resume', value='Resume song', inline=False)
  embed.add_field(name='skip', value='Skip to next song in queue', inline=False)
  embed.add_field(name='stop', value='Stop song', inline=False)
  embed.add_field(name='clear', value='Clear message(s)', inline=False)

  await ctx.send(embed=embed)


@client.command()
async def hello(ctx):
  await ctx.send('Hello I\'m Boomby, a self made music bot for personal use!')


@client.command(pass_context = True)
async def join(ctx):
  if (ctx.author.voice):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    
    if voice and voice.is_connected():
      await voice.move_to(channel)
    else:
      voice = await channel.connect()      
    
    await ctx.send(':dancer: `Joined!`')
  else:
    await ctx.send(':angry: `You are not in a voice channel`')


@client.command(pass_context = True)
async def leave(ctx):
  if (ctx.voice_client):
    await ctx.guild.voice_client.disconnect()
    await ctx.send(':smiling_face_with_tear: `Leaving`')
  else:
    await ctx.send(':confused: `Deemo is not in a voice channel`')


@client.command(pass_context = True)
async def queue(ctx):
    local_queue = queues[ctx.message.guild.id]
    for i in range(len(local_queue)):
        await ctx.send(local_queue[i])

@client.command(pass_context = True)
async def play(ctx, *, url):
  if (ctx.author.voice):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
      await voice.move_to(channel)
    else:
      voice = await channel.connect()
  else:
    await ctx.send('`You are not in a voice channel`')
  
  YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'default_search':"ytsearch"}
  FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
  voice = get(client.voice_clients, guild=ctx.guild)
  
  with YoutubeDL(YDL_OPTIONS) as ydl:
      info = ydl.extract_info(url, download=False)
      
      if 'entries' in info:
        url = info["entries"][0]["formats"][0]['url']
      elif 'formats' in info:
        url = info["formats"][0]['url']
  
  title = info.get('title')
  if title == None:
    title = info['entries'][0]['title']        
  
  source = (FFmpegPCMAudio(url, **FFMPEG_OPTIONS))
  
  if voice.is_playing():
    guild_id = ctx.message.guild.id
    
    if guild_id in queues:
      queues[guild_id].append(source)
    else:
      queues[guild_id] = [source]

    embed_q = discord.Embed(colour = discord.Colour.magenta())
    embed_q.add_field(name='『  '+str(title) + '  』added to queue', value='『'+ctx.author.mention+'』' , inline=False)
    await ctx.send(embed=embed_q)    
  else:
      voice.play(FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda x=0: check_queue(ctx, ctx.message.guild.id))
      embed_p = discord.Embed(colour = discord.Colour.magenta())
      embed_p.add_field(name=':headphones: Playing:『  ' + str(title)+' 』', value='『'+ctx.author.mention+'』' , inline=False)
      await ctx.send(embed=embed_p)


@client.command(pass_context = True)
async def pause(ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if not (ctx.author.voice):
    await ctx.send('`You are not in voice`')
  else:  
    if voice.is_playing():
      voice.pause()
      await ctx.send(':pause_button: `Paused`')
    else:
      await ctx.send('`Currently playing no audio`') 
   
      
@client.command(pass_context = True)
async def resume(ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if not (ctx.author.voice):
    await ctx.send('`You are not in voice`')
  else:  
    if voice.is_paused():
      voice.resume()
      await ctx.send(':play_pause: `Resume`')
    else:
      await ctx.send("`The audio is not pause`")


@client.command(pass_context = True)
async def skip(ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if not (ctx.author.voice):
    await ctx.send('`You are not in voice`')
  else:
    if voice.is_playing():
      voice.stop()
      await ctx.send(':track_next: `Skipped..`')
    else:
      await ctx.send('`Currently playing no audio`')


@client.command(pass_context = True)
async def stop(ctx):
  await ctx.guild.voice_client.disconnect()
  if (ctx.author.voice):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
      await voice.move_to(channel)
    else:
      voice = await channel.connect()   
    await ctx.send(':stop_button: `Stop playing`')


@client.command()
async def clear(ctx, amount=5):
  await ctx.channel.purge(limit=amount+1)
  await ctx.send(':x: `Messages deleted`')
  time.sleep(3)
  await ctx.channel.purge(limit=1)    



keep_alive()
client.run('OTA1MDM5NDI5OTM5MzYzODYw.YYERpg.4AvnfiWowL7ZvxSPvyt7g5EXZfU')
