from threading import local
import discord
import os
import time
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from keep_alive import keep_alive
from music import music 

intents = discord.Intents.default()
intents.members = True

music_queues = {}
null_music_data = {'source' : None, 'title' : 'Null', 'requestor' : None}
currently_playing = null_music_data

def play_next_in_queue(ctx, guild_id):
    queue = music_queues[guild_id]
    
    if queue != []:
        voice = ctx.guild.voice_client
        music_data = queue.pop(0)
        
        global currently_playing 
        currently_playing = music_data
        
        voice.play(music_data['source'], after=lambda x=0: play_next_in_queue(ctx, guild_id))
    else:
        currently_playing = null_music_data
        
        
        
client = commands.Bot(command_prefix = '!', intents=intents, help_command=None)

@client.event
async def on_ready():
    activity = discord.Game(name='Boomby')
    await client.change_presence(status=discord.Status.online, activity=activity)
    print('Logged in as {0.user}'.format(client))
    print('-------------------')


# ----------------------------------- help ----------------------------------- #
@client.command(pass_context = True)
async def help(ctx):
    embed = discord.Embed(colour = discord.Colour.magenta())
    embed.set_author(name='Command prefix: !')
    embed.add_field(name='help', value='Show available commands.', inline=False)
    
    embed.add_field(name='join', value='Adds Boomby to your voice-channel. You must be connected to the voice-channel before running this command.', inline=False)
    embed.add_field(name='disconnect', value='Removes Boomby from your voice-channel.', inline=False)    
    
    embed.add_field(name='play, p [url/name]', value='Plays the song or adds to queue if there are already songs playing.', inline=False)
    embed.add_field(name='remove, rm [queue_index]', value='Removes the song from the queue. Use !queue to find its queue_index.', inline=False)
    embed.add_field(name='queue, q', value='Displays the current song playing and upcoming songs in queue.', inline=False)
    
    embed.add_field(name='pause, ps', value='Pauses current song.', inline=False)
    embed.add_field(name='resume, r', value='Resumes current song.', inline=False)
    embed.add_field(name='skip, s', value='Skips to next song in queue.', inline=False)
    embed.add_field(name='stop, st', value='Stops current song and clears queue.', inline=False)
    
    embed.add_field(name='clear', value='Clears message(s)', inline=False)

    await ctx.send(embed=embed)
# ------------------------------------- - ------------------------------------ #

# ----------------------------------- hello ---------------------------------- #
@client.command()
async def hello(ctx):
    await ctx.send('Hello I\'m Boomby, a self made music bot for personal use!')
# ------------------------------------- - ------------------------------------ #

# ---------------------------------- play, p --------------------------------- #
async def fplay(ctx, url):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
    else:
        await ctx.send(':angry: You are not in a voice channel!')
  
  
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
   
    music_data = {
        'source' : source,
        'title' : str(title),
        'requestor' : ctx.message.author
    }
    
    if voice.is_playing():
        guild_id = ctx.message.guild.id

        if guild_id in music_queues:
            music_queues[guild_id].append(music_data)
        else:
            music_queues[guild_id] = [music_data]

        embed_q = discord.Embed(colour = discord.Colour.magenta())
        embed_q.add_field(name=str(title) + ' added to queue', value=ctx.author.mention, inline=False)
        await ctx.send(embed=embed_q)    
    else:
        global currently_playing
        currently_playing = music_data
        
        voice.play(FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda x=0: play_next_in_queue(ctx, ctx.message.guild.id))
        embed_p = discord.Embed(colour = discord.Colour.magenta())
        embed_p.add_field(name=':headphones: Playing: ' + str(title), value=ctx.author.mention, inline=False)
        await ctx.send(embed=embed_p)
    

@client.command(pass_context = True)
async def play(ctx, *, url):
    await fplay(ctx, url)
@client.command(pass_context = True)
async def p(ctx, *, url):
    await fplay(ctx, url)
# ------------------------------------- - ------------------------------------ #

# -------------------------------- remove, rm -------------------------------- #
async def fremove(ctx, index=0):
    if ctx.message.guild.id in music_queues:
        local_queue = music_queues[ctx.message.guild.id]
        index = int(index)
        
        if index == 0:
            index = len(local_queue)
        else:
            index -= 1
        
        music_data = local_queue[index]
        if music_data:
            local_queue.pop(index)
            await ctx.send("Removed: " + music_data['title'] + " from queue!")    

@client.command(pass_context = True)
async def remove(ctx, index):
    await fremove(ctx, index)
@client.command(pass_context = True)
async def rm(ctx, index):
    await fremove(ctx, index)
# ------------------------------------- - ------------------------------------ #

# --------------------------------- pause, ps -------------------------------- #
async def fpause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not (ctx.author.voice):
        await ctx.send(':angry; You are not in voice channel!')
    else:  
        if voice.is_playing():
            voice.pause()
            await ctx.send(':pause_button: Paused: ' + currently_playing['title'])
        else:
            await ctx.send(':confused: Currently playing no audio') 
            
@client.command(pass_context = True)
async def pause(ctx):
    await fpause(ctx)
@client.command(pass_context = True)
async def ps(ctx):
    await fpause(ctx)
# ------------------------------------- - ------------------------------------ #

# --------------------------------- resume, r -------------------------------- #
async def fresume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not (ctx.author.voice):
        await ctx.send(':angry: You are not in voice channel!')
    else:  
        if voice.is_paused():
            voice.resume()
            await ctx.send(':play_pause: Resumed: ' + currently_playing['title'])
        else:
            await ctx.send(":confused: The audio is not paused..?")

@client.command(pass_context = True)
async def resume(ctx):
    await fresume(ctx)
@client.command(pass_context = True)
async def r(ctx):
    await fresume(ctx)
# ------------------------------------- - ------------------------------------ #

# ---------------------------------- skip, s --------------------------------- #
async def fskip(ctx):
    global currently_playing
    
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not (ctx.author.voice):
        await ctx.send(':angry: You are not in a voice-channel!')
    else:
        if voice.is_playing():
            voice.stop()
            await ctx.send(':track_next: Skipped: ' + currently_playing['title'])
        else:
            currently_playing =  null_music_data
            await ctx.send(':rofl: No more music to skip!')

@client.command(pass_context = True)
async def skip(ctx):
    await fskip(ctx)
@client.command(pass_context = True)
async def s(ctx):
    await fskip(ctx)
# ------------------------------------- - ------------------------------------ #

# --------------------------------- queue, q --------------------------------- #
async def fqueue(ctx):
    if currently_playing == null_music_data:
        await ctx.send(':cricket: Nothing playing or in queue')
    else:
        embed = discord.Embed(colour = discord.Colour.magenta())
        embed.add_field(name=':microphone: Now playing: ' + currently_playing['title'], value='Requested by :' + currently_playing['requestor'].mention, inline=False)
        embed.add_field(name='Up next:', value=':parrot:', inline = False)
        if ctx.message.guild.id in music_queues:
            local_queue = music_queues[ctx.message.guild.id]
            for i in range(len(local_queue)):
                music_data = local_queue[i]
                embed.add_field(name=str((i+1))+') ' + music_data['title'], value='Requested by: ' + music_data['requestor'].mention, inline=False)

        await ctx.send(embed = embed)

@client.command(pass_context = True)
async def queue(ctx):
    await fqueue(ctx)    

@client.command(pass_context = True)
async def q(ctx):
    await fqueue(ctx)
# ------------------------------------- - ------------------------------------ #

# --------------------------------- stop, st --------------------------------- #
async def fstop(ctx, end = False):
    global currently_playing
    currently_playing = null_music_data
    
    if ctx.message.guild.id in music_queues:
        music_queues[ctx.message.guild.id] = []
    
    await ctx.guild.voice_client.disconnect()
    
    if not end:
        if (ctx.author.voice):
            channel = ctx.message.author.voice.channel
            voice = get(client.voice_clients, guild=ctx.guild)
            if voice and voice.is_connected():
                await voice.move_to(channel)
            else:
                voice = await channel.connect()   
                await ctx.send(':stop_button: Stopped playing!')

@client.command(pass_context = True)
async def stop(ctx):
    await fstop(ctx)
@client.command(pass_context = True)
async def st(ctx):
    await fstop(ctx)
# ------------------------------------- - ------------------------------------ #

# --------------------------------- join, disconnect --------------------------------- #
@client.command(pass_context = True)
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)
    
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()      
    
        await ctx.send(':dancer: Joined!')
    else:
        await ctx.send(':angry: You are not in a voice channel')


@client.command(pass_context = True)
async def disconnect(ctx):
    if (ctx.voice_client):
        await fstop(ctx, True)
        await ctx.guild.voice_client.disconnect()
        await ctx.send(':smiling_face_with_tear: Leaving')
    else:
        await ctx.send(':confused: Deemo is not in a voice channel')
# ------------------------------------- - ------------------------------------ #

# ----------------------------------- clear ---------------------------------- #
@client.command()
async def clear(ctx, count=5):
    await ctx.channel.purge(limit=count+1)
    await ctx.send(':x: Messages deleted!')
    time.sleep(5)
    await ctx.channel.purge(limit=1)    
# ------------------------------------- - ------------------------------------ #


keep_alive()
client.run('OTA1MDM5NDI5OTM5MzYzODYw.YYERpg.hh3XrY8LLQfOwohbSjecmADtqXg')