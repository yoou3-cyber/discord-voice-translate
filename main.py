import os
import discord
from discord.ext import commands
import requests
import speech_recognition as sr 
from pydub import AudioSegment
from config import token, prefix

bot = commands.Bot(command_prefix=prefix, intents=disсord.Intents.all())

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

@bot.command(name="voice", description="Translate voice message to text") #main command "voice" for translating
async def voice(ctx):
    if ctx.message.reference.resolved.attachments:
        attachment = ctx.message.reference.resolved.attachments[0].url
        if attachment.endswith('.ogg'):
            response = requests.get(attachment)
            name = ctx.author.name
            
            with open(f'{ctx.author.name}.ogg', 'wb') as f:
                f.write(response.content)

            audio = AudioSegment.from_file(f'{name}.ogg', format='ogg')
            audio.export(f'{name}.wav', format='wav')

            r = sr.Recognizer()
            with sr.AudioFile(f'{name}.wav') as source:
                audio = r.record(source)

            try:
                text = r.recognize_google(audio, language='ru-RU')

                await ctx.reply(f'Text from voice:\n> "{text}"')
                os.remove(f'{name}.ogg')
                os.remove(f'{name}.wav')
            except sr.UnknownValueError:
                await ctx.reply('Text not recognized')
        else:
            await ctx.reply(f'Message is not an voice message')
    else:
        await ctx.reply(f'Message is not an voice message')   

@bot.message_command(name="voice2text")  #context-menu command
async def get_message_id(ctx, message: discord.Message): 
    if message.attachments:
        attachment = message.attachments[0].url
        if attachment.endswith('.ogg'):
                
            response = requests.get(attachment)
            name = message.author.name
            
            with open(f'{name}.ogg', 'wb') as f:
                f.write(response.content)

            audio = AudioSegment.from_file(f'{name}.ogg', format='ogg')
            audio.export(f'{name}.wav', format='wav')

            r = sr.Recognizer()
            with sr.AudioFile(f'{name}.wav') as source:
                audio = r.record(source)

            try:
                text = r.recognize_google(audio, language='ru-RU')

                await ctx.respond(f'Text from voice:\n> "{text}"\noriginal message: {message.jump_url}')
                os.remove(f'{name}.ogg')
                os.remove(f'{name}.wav')
            except sr.UnknownValueError:
                await ctx.respond('Text not recognized', ephemeral=True)
        else:
            await ctx.reply(f'Message is not an voice message', ephemeral=True)
    else:
        await ctx.reply(f'Message is not an voice message', ephemeral=True)     


@bot.command(name="set-auto") #setup auto-translate for guild
async def setup(ctx):
    with open('auto.json', 'r') as f:
        data = json.load(f)
    data[str(ctx.guild.id)] = True
    with open('auto.json', 'w') as f:
        json.dump(data, f, indent=4)
    await ctx.send(f"Now bot will translate every voice message automatically")

@bot.command(name="unset-auto") #unset auto-translate for guild
async def setup(ctx):
    with open('auto.json', 'r') as f:
        data = json.load(f)
    data[str(ctx.guild.id)] = False
    with open('auto.json', 'w') as f:
        json.dump(data, f, indent=4)
    await ctx.send(f"Bot no longer translates automatically")

@bot.event #auto-translate for guild in auto.json
async def on_message(message):
    with open('auto.json', 'r') as f:
        data = json.load(f)
    if str(message.guild.id) in data:
        if data[str(message.guild.id)] == True:
            if message.attachments:
                attch = message.attachments[0].url
                if attch.endswith('.ogg'):
                    response = requests.get(attch)
                    name = message.author.name
                    
                    with open(f'{message.author.name}.ogg', 'wb') as f:
                        f.write(response.content)

                    audio = AudioSegment.from_file(f'{name}.ogg', format='ogg')
                    audio.export(f'{name}.wav', format='wav')

                    r = sr.Recognizer()
                    with sr.AudioFile(f'{name}.wav') as source:
                        audio = r.record(source)

                    try:
                        text = r.recognize_google(audio, language='ru-RU')

                        await message.reply(f'Text from voice:\n> "{text}"')
                        os.remove(f'{name}.ogg')
                        os.remove(f'{name}.wav')
                    except sr.UnknownValueError:
                        await message.reply('Text not recognized')
    await bot.process_commands(message) 

bot.run(token) #run bot
