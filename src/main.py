#!/media/Programming/repos/py/_discord_bots/Boomby/venv/bin/python   
from random import random
from threading import local
import time

import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import CommandNotFound
from discord import FFmpegPCMAudio
from discord import Status

from youtube_dl import YoutubeDL
from keep_alive import keep_alive

#token
from bot_token import str_token

intents = discord.Intents.default()
intents.members = True
intents.messages = True

music_queues = {}
null_music_data = {'source' : None, 'title' : 'Null', 'requestor' : None}
currently_playing = {}

def play_next_in_queue(ctx, guild_id):
    queue = music_queues[guild_id]
    
    if queue != []:
        voice = ctx.guild.voice_client
        music_data = queue.pop(0)
        
        global currently_playing 
        currently_playing[guild_id] = music_data
        
        voice.play(music_data['source'], after=lambda x=0: play_next_in_queue(ctx, guild_id))
    else:
        currently_playing[guild_id] = null_music_data
        
        
client = commands.Bot(command_prefix = '!', intents=intents, help_command=None, case_insensitive=True)

@client.event
async def on_ready():
    activity = discord.Game(name='Boomby')
    await client.change_presence(status=discord.Status.online, activity=activity)
    print('Logged in as {0.user}'.format(client))
    print('-------------------')


@client.event
async def on_command_error(ctx, error):
    await ctx.send(":warning: Unknown command used. Please see `!help` for commands list and respective usage.")
    if isinstance(error, CommandNotFound):
        return
    raise error

# ----------------------------------- help ----------------------------------- #
@client.command(pass_context = True)
async def help(ctx):
    embed = discord.Embed(colour = discord.Colour.magenta())
    embed.set_author(name='Command prefix: !')
    embed.add_field(name='help', value='Show available commands.', inline=False)
    
    embed.add_field(name='join, j', value='Adds Boomby to your voice-channel. You must be connected to the voice-channel before running this command.', inline=False)
    embed.add_field(name='disconnect, d', value='Removes Boomby from your voice-channel.', inline=False)    
    
    embed.add_field(name='play, p [url/name]', value='Plays the song or adds to queue if there are already songs playing.', inline=False)
    embed.add_field(name='remove, rm [queue_index]', value='Removes the song from the queue. Use !queue to find its queue_index. A queue index of -1 will remove the most recently added song from queue.', inline=False)
    embed.add_field(name='queue, q', value='Displays the current song playing and upcoming songs in queue.', inline=False)
    
    embed.add_field(name='pause, ps', value='Pauses current song.', inline=False)
    embed.add_field(name='resume, rs', value='Resumes current song.', inline=False)
    embed.add_field(name='skip, s', value='Skips to next song in queue.', inline=False)
    embed.add_field(name='stop, st', value='Stops current song and clears queue.', inline=False)
    
    embed.add_field(name='clear', value='Clears message(s)', inline=False)

    await ctx.send(embed=embed)
# ------------------------------------- - ------------------------------------ #

# -------------------------------- isConnected ------------------------------- #
async def send_if(ctx, check, message):
    if check:
        await ctx.send(message)
        
async def is_connected(ctx, user_connected = True, send_assert = False):
    if user_connected and not ctx.author.voice:
        await send_if(ctx, send_assert, ':angry: You are not in a voice channel!')
        return False

    voice = get(client.voice_clients, guild=ctx.guild)
    
    if voice and voice.is_connected():
        
        if user_connected and voice.channel != ctx.message.author.voice.channel:
            await send_if(ctx, send_assert, ':angry: You are not in the same voice channel as Boomby!')
            return False
        
        return True

    await send_if(ctx, send_assert, ':confused: Boomby is not in a voice channel.. Use `!join` first.')
    return False
# ------------------------------------- - ------------------------------------ #

# ---------------------------------- play, p --------------------------------- #
def fformat(dur):
    hours, rem = divmod(dur, 3600)
    minutes, seconds = divmod(rem, 60)
    return '{:0>2}h:{:0>2}m:{:02}s'.format(int(hours),int(minutes),seconds)
    
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
  
  
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'default_search':'ytsearch'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = get(client.voice_clients, guild=ctx.guild)
  
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)

        o_url = url
        if 'entries' in info:
            url = info['entries'][0]['formats'][0]['url']
            duration = fformat(int(info['entries'][0]['duration']))
            short_url = info['entries'][0]['webpage_url']
        elif 'formats' in info:
            url = info['formats'][0]['url']
            duration = None
            short_url = None
            
    title = info.get('title') or info['entries'][0]['title']
    
    source = (FFmpegPCMAudio(url, **FFMPEG_OPTIONS))
    guild_id = ctx.message.guild.id
   
    music_data = {
        'source' : source,
        'title' : str(title),
        'requestor' : ctx.message.author
    }
    
    embed = discord.Embed(colour = discord.Colour.magenta(), url = (short_url and url) or o_url)
    if duration:
        embed.add_field(name='Length:', value=str(duration))
    embed.add_field(name='Requested by:', value=ctx.author.mention)
    
    if voice.is_playing():
        embed.title = 'Queued: ' + str(title)
        if guild_id in music_queues:
            music_queues[guild_id].append(music_data)
        else:
            music_queues[guild_id] = [music_data]
    else:
        embed.title = ':headphones: Now playing: ' + str(title)
        global currently_playing
        currently_playing[guild_id] = music_data
        voice.play(FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda x=0: play_next_in_queue(ctx, ctx.message.guild.id))

    await ctx.send(embed=embed)    
    await send_if(ctx, short_url, short_url)
    

@client.command(pass_context = True)
async def play(ctx, *, url):
    await fplay(ctx, url)
@client.command(pass_context = True)
async def p(ctx, *, url):
    await fplay(ctx, url)
# ------------------------------------- - ------------------------------------ #

# -------------------------------- remove, rm -------------------------------- #
async def fremove(ctx, index=0):
    if await is_connected(ctx, user_connected=True, send_assert=True):
        if ctx.message.guild.id in music_queues:
            local_queue = music_queues[ctx.message.guild.id]
            index = int(index)
            index = (index == -1 and len(local_queue) - 1) or (index-1)            
            
            if index < 0 or index >= len(local_queue):
                await ctx.send(':warning: Queue index is out of range. \n\nPlease use `!queue` first to find the correct queue index. A queue index of -1 would remove the most recently added song to queue')
            else:
                music_data = local_queue[index]
                if music_data:
                    local_queue.pop(index)
                    await ctx.send('Removed: ' + music_data['title'] + ' from queue!')    

@client.command(pass_context = True)
async def remove(ctx, index):
    await fremove(ctx, index)
@client.command(pass_context = True)
async def rm(ctx, index):
    await fremove(ctx, index)
# ------------------------------------- - ------------------------------------ #

# --------------------------------- pause, ps -------------------------------- #
async def fpause(ctx):
    if await is_connected(ctx, user_connected=True, send_assert=True):
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
            await ctx.send(':pause_button: Paused: ' + currently_playing[ctx.message.guild.id]['title'])
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
    if await is_connected(ctx, user_connected=True, send_assert=True):
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
            await ctx.send(':play_pause: Resumed: ' + currently_playing[ctx.message.guild.id]['title'])
        else:
            await ctx.send(':confused: The audio is not paused..?')

@client.command(pass_context = True)
async def resume(ctx):
    await fresume(ctx)
@client.command(pass_context = True)
async def rs(ctx):
    await fresume(ctx)
# ------------------------------------- - ------------------------------------ #

# ---------------------------------- skip, s --------------------------------- #
async def fskip(ctx):
    if await is_connected(ctx, user_connected=True, send_assert=True):
        global currently_playing    
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.stop()
            await ctx.send(':track_next: Skipped: ' + currently_playing[ctx.message.guild.id]['title'])
        else:
            currently_playing[ctx.message.guild.id] =  null_music_data
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
    if await is_connected(ctx, user_connected=True, send_assert=True):
        guild_id = ctx.message.guild.id
        if not currently_playing[guild_id] or currently_playing[guild_id] == null_music_data:
            await ctx.send(':cricket: Nothing playing or in queue')
        else:
            embed = discord.Embed(colour = discord.Colour.magenta())
            embed.add_field(name=':microphone: Now playing: ' + currently_playing[guild_id]['title'], value='Requested by :' + currently_playing[guild_id]['requestor'].mention, inline=False)
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
async def clear_queue(ctx, clear_active = False):
    if clear_active:
        global currently_playing
        currently_playing[ctx.message.guild.id] = null_music_data
    
    if ctx.message.guild.id in music_queues:
        music_queues[ctx.message.guild.id] = []

    await ctx.send('Queue has been cleared!')

async def fstop(ctx):
    if await is_connected(ctx, user_connected=True, send_assert=True):
        await clear_queue(ctx, True)
        await ctx.guild.voice_client.disconnect()

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
async def fjoin(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)
        guild_id = ctx.message.guild.id
        
        #await clear_queue(ctx)
        if voice and voice.is_connected():
            if voice.channel != channel:
                await voice.move_to(channel)
            else:
                await ctx.send(':confused: Boomby is already connected to your voice channel.')
                return
        else:
            voice = await channel.connect()      

        currently_playing[guild_id] = null_music_data
        music_queues[guild_id] = []
        await ctx.send(':dancer: Joined!')
    else:
        await ctx.send(':angry: You are not in a voice channel')

@client.command(pass_context = True)
async def join(ctx):
    await fjoin(ctx)

@client.command(pass_context = True)
async def j(ctx):
    await fjoin(ctx)


async def fdisconnect(ctx):
    if await is_connected(ctx, user_connected=True, send_assert=True):
        await clear_queue(ctx, True)
        await ctx.guild.voice_client.disconnect()
        await ctx.send(':smiling_face_with_tear: Leaving')
        
@client.command(pass_context = True)
async def disconnect(ctx):
    await fdisconnect(ctx)
    
@client.command(pass_context = True)
async def d(ctx):
    await fdisconnect(ctx)
# ------------------------------------- - ------------------------------------ #

# ----------------------------------- clear ---------------------------------- #
@client.command()
async def clear(ctx, count=5):
    await ctx.channel.purge(limit=count+1)
    await ctx.send(':x: Messages deleted!')
    time.sleep(1)
    await ctx.channel.purge(limit=1)    
# ------------------------------------- - ------------------------------------ #


keep_alive()
client.run(str_token)