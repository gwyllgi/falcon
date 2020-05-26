import discord
import wikipedia
import asyncio
import youtube_dl
import random
import os
from discord.ext.commands import Bot
from discord.utils import get
from discord.ext import commands


language = "id"

import settings as discord_settings
from utils import search_google
from db import setup_db_table, create_search_history, get_search_history

bot = commands.Bot(command_prefix='/')

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,activity=discord.Game('/cmd untuk menampilkan list command bosque'))
    print("Bot-nya sudah jalan bosque!")

    
@bot.command(name='fs', help='Menampilkan Hasil Pencarian Google (3 Baris) ')
async def google_bot(ctx, *args):
    # validate user input
    if not args:
        await ctx.send(discord_settings.INPUT_REQUIRED_ERROR_MSG)
    else:
        search_keyword = ' '.join(args)
        # validate if input is less than or equal to 255 characters
        if len(search_keyword) > discord_settings.INPUT_MAX_LENGTH:
            await ctx.send(discord_settings.MAX_LENGTH_ERROR_MSG)
        else:
            # create entry in database
            create_search_history(search_keyword)
            # get result from google api
            results = search_google(search_keyword)
            if not results:
                await ctx.send(discord_settings.GOOGLE_NO_RESULT_MSG)
            for result in results:
                embed = discord.Embed(
                    title=result.get('title'),
                    url=result.get('link'),
                    description=result.get('description'),
                    color=discord_settings.EMBED_COLOR,
                )
                await ctx.send(embed=embed)


@bot.command(name='fr', help='Menampilkan kembali hasil pencarian 5 terakhir ')
async def search_history_bot(ctx, *args):
    # validate user input
    if not args:
        await ctx.send(discord_settings.INPUT_REQUIRED_ERROR_MSG)
    else:
        search_keyword = ' '.join(args)
        # validate if input is less than or equal to 255 characters
        if len(search_keyword) > discord_settings.INPUT_MAX_LENGTH:
            await ctx.send(discord_settings.INPUT_REQUIRED_ERROR_MSG)
        else:
            search_history = get_search_history(search_keyword)
            if search_history:
                search_history = ['**Riwayat Pencarian**'] + search_history
            else:
                search_history = ['**Hasil tidak ditemukan**']
            await ctx.send('\n'.join(search_history))

@bot.command(name='fabout', help='Menampilkan credit ')
async def search_history_bot(ctx, *args):
	await ctx.send('Developed by MrRaptor')

@bot.command(name='ping', help='Cek respon time ')
async def ping(ctx): 
    await ctx.send(f'Response time : {round(bot.latency * 1000)} ms')

@bot.command(name='wiki', help='Pencarian Wikipedia ')
async def wikiSum(ctx,userInput):
    try: 
            await ctx.send(format(wikipedia.summary(userInput,sentences=4)))
    except wikipedia.exceptions.DisambiguationError as e:
            await ctx.send(format(("Error: {0}".format(e))))
            await ctx.send("Error: terlalu banyak hasil pencarian, tolong lebih detail.")

    wikipedia.set_lang("id")

@bot.command(name='wikipic', help='Pencarian Wikipedia dengan Gambar')
async def wikiPic(ctx,userInput):
    try:
          picFind = wikipedia.page(userInput)
          await ctx.send("Picture from: <{}>".format(picFind.url))
          await ctx.send(picFind.images[6])
          await ctx.send(format(wikipedia.summary(userInput,sentences=4)))

    except wikipedia.exceptions.DisambiguationError as e:
            await ctx.send(format(("Error: {0}".format(e))))
            await ctx.send("Silahkan coba dengan lebih detail.")

    wikipedia.set_lang("id")

@bot.command(name='cmd', help='bantuan untuk command list')
async def self(ctx): #command !help gives list of all commands
        commands={}
        commands['/cmd']='Menampilkan menu ini'
        commands['/fs <keyword>']='Menampilkan hasil pencarian dari Google'
        commands['/fr <keyword>']='Menampilkan riwayat pencarian dari Google'
        commands['/fabout']='Menampilkan Credits'
        commands['/ping']='Melihat response time'
        commands['/wiki <keyword>']='Pencarian dalam Wikipedia'
        commands['/wikipic <keyword>']='Pencarian dengan Gambar dalam Wikipedia'
        commands['/clear']= 'Hapus pesan (Default 5)'

        msg=discord.Embed(title='Falcon Commands', description="Developed by MrRaptor#8460",color=0xff99ff)

        for command,description in commands.items():
            msg.add_field(name=command,value=description, inline=False)
            
        await ctx.send(embed=msg)

@bot.command(name='clear', help='Menghapus pesan')
async def clear(ctx,amount=5):
    await ctx.channel.purge(limit=amount)

@google_bot.error
@search_history_bot.error
async def info_error(ctx, error):
    await ctx.send('Terjadi kesalahan. Error - {}'.format(error))

#YOUTUBE MUSIC

@bot.command(name='queue', help='Antrian Lagu')
async def queue(ctx, url: str):
     Queue_infile = os.path.isdir("./Queue")
     if Queue_infile is False:
         os.mkdir("Queue")
     DIR = os.path.abspath(os.path.realpath("Queue"))
     q_num = len(os.listdir(DIR))
     q_num += 1
     add_queue = True
     while add_queue:
         if q_num in queue:
             q_num += 1
         else:
             add_queue = False
             queues[q_num] = q_num
     queue_path = os.path.abspath(os.path.realpath("Queue"))
     ydl_opts = {
          'format': 'bestaudio/best',
          'quiet': True,
          'outtmpl': queue_path,
          'postprocessors':[{
             'key':'FFmpegExtractAudio',
             'preferredcodec':'mp3',
             'preferredquality':'192',
         }]
     }
     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
         print('Downloading audio now\n')
         ydl.download([url])
     await ctx.send("Aku menambahkan lagu " + str(q_num) + " ke antrian")
     print("Lagu telah dimasukan ke antrian")

@bot.command(name='join', help='Join Voice Channel')
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    await ctx.send(f"Aku join{channel}")

@bot.command(name='leave', help='Keluar voice channel')
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"Ops! aku keluar dari {channel}")
        await ctx.send(f"Goodbye!")
    else:
        print("Katanya disuruh keluar tapi tidak masuk channel")
        await ctx.send("Tidak dalam voice channel")

@bot.command(name='play', help='Play [url]')
async def play(ctx, url: str):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    
    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("Tidak ada lagi antrian\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Lagu selesai, memutar antrian selanjutnya\n")
                print(f"Lagu masih dalam antrian : {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')
                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 1
            else:
                queues.clear()
                return
        else:
            queues.clear()
            print("Tidak ada lagu antrian sesudah lagu ini selesai.\n")
    previous_song = os.path.isfile("song.mp3")
    try:
        if previous_song:
            os.remove("song.mp3")
            queues.clear()
            print("Menghapus lagu exp")
    except PermissionError:
        print('Mencoba hapus file lagu, tapi masih dalam pemutaran')
        await ctx.send("Gass {0.display_name}, Aku putarkan lagu untukmu".format(ctx.author))
        return
    
    Queue_infile = os.path.isdir("./Queue")

    try:
        Queue_folder = ("./Queue")
        if Queue_infile is True:
            print("Hapus folder antrian exp")
            shutil.rmtree(Queue_folder)
    except:
        print("Tidak ada folder antrian exp")

    await ctx.send("Silahkan tunggu!") 

    voice = get(bot.voice_clients, guild = ctx.guild)
    ydl_opts = {
         'format': 'bestaudio/best',
         'quiet': True,
         'postprocessors':[{
            'key':'FFmpegExtractAudio',
            'preferredcodec':'mp3',
            'preferredquality':'192',
        }]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('Downloading audio now\n')
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")
    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 70

    nname = name.rsplit(" ", 2)
    await ctx.send(f"Playing: {nname}")
    print("Playing\n")

@bot.command(name='pause', help='Pause Lagu')
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        print("Lagu paused")
        voice.pause()
        await ctx.send("Jangan panik, saya jeda lagunya")
    else:
        print("Lagu tidak memutar")
        await ctx.send("Silly {0.display_name}, tidak ada lagu yang terputar sekarang".format(ctx.author))

@bot.command(name='resume', help='Resume Lagu')
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        print("Resume lagu")
        voice.resume()
        await ctx.send("Aku melanjutkan putar lagu")
    else:
        print("Lagu tidak terjeda.")
        await ctx.send("Aku tidak menjeda lagu.")

@bot.command(name='stop', help='Stop Lagu')
async def stop(ctx):

    queues.clear()

    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        print("Menghentikan Lagu")
        voice.stop()
        await ctx.send("Lagu tidak dapat dihentikan (protected)")
    else:
        print("Lagu masih tetap terputar.")
        await ctx.send("Silly {0.display_name}, tidak ada lagu yang terputar sekarang".format(ctx.author))
  
 
if __name__ == '__main__':
    setup_db_table()
    bot.run(discord_settings.TOKEN)
