import discord
import os
import ctx
from discord.ext import commands, tasks
from discord import FFmpegPCMAudio
from discord.utils import get
from discord import member
import asyncio
from asyncio import queues
from itertools import cycle
import random
import time
import math
from typing import Union
from random import randint, randrange
import configparser
import sys
import hashlib
import gtts
from playsound import playsound
import base64
from update_check import isUpToDate
from update_check import update

# Einstellungen laden

config = configparser.ConfigParser()
config.read('SETTINGS.INI', encoding='utf-8')
config2 = configparser.ConfigParser()
config2.read('TOKEN.INI', encoding='utf-8')
#print(config['GLOBAL']['status1'])

status1 = config['GLOBAL']['status1']
status2 = config['GLOBAL']['status2']
status3 = config['GLOBAL']['status3']
status4 = config['GLOBAL']['status4']
prefix = config['GLOBAL']['prefix']
sendrole = config['ROLES']['send']
warnrole = config['ROLES']['warn']
clearrole = config['ROLES']['clear']
modrole = config['ROLES']['mod']
banrole = config['ROLES']['ban']
kickrole = config['ROLES']['kick']
welcomech = int(config['CHANNELS']['welcome'])
warnch = int(config['CHANNELS']['log'])
verifych = int(config['CHANNELS']['verify'])
verifysuc = config['MESSAGES']['verifysuc'].replace('BREAK', '\n')
verifybadpin = config['MESSAGES']['verifybadpin']
language = config['GLOBAL']['language']
token = config2['TOKEN']['token']

#Einstellungen geladen

intents = discord.Intents.default()
intents.members = True
intents.messages = True

botversion = config['GLOBAL']['version']
description = '''Bot'''

bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.remove_command('help')
status = cycle([status1, status2, status3, status4])

@bot.event
async def on_ready():
    print('------')  
    print('Version: ' + botversion)
    print('Bot gestartet, eingeloggt als:')
    print(bot.user.name)
    print(bot.user.id)
    print('Sprache: {}'.format(language))
    print('(c)2021 TW Service')
    print('------')
    await bot.change_presence(activity=discord.Game(name=status1))

@bot.command(pass_context=True, aliases=['Verify'])
async def verify(ctx, pin: int):
    with open('pins.txt', 'r') as file:
        data = file.read()
    print(data)
    member = ctx.message.author
    channel = ctx.message.channel
    if str(pin) == data :
        print(f'{member.name} is now verified')
        role = discord.utils.get(member.guild.roles, name='Verifiziert')
        await member.add_roles(role)
        messages = []
        async for message in channel.history(limit=100):
                messages.append(message)
        await channel.delete_messages(messages)
        await member.send(verifysuc)
        dir = "."
        files = os.listdir(dir)
        for file in files:
            if file.endswith(".m4a"):
                os.remove(os.path.join(dir,file))
    else :
        await channel.send(verifybadpin)

@bot.command(pass_context=True, aliases=['Clear'])
@commands.has_role(clearrole)
async def clear(ctx, amount: int):
    channel = ctx.message.channel
    messages = []
    async for message in channel.history(limit=amount):
              messages.append(message)
    await channel.delete_messages(messages)
    print('Log: Cleared {} Message(s)!'.format(amount))
    
@bot.event
async def on_member_join(member):
    pin = randint(100000, 999999)
    fname = randint(10, 99)
    file = open("pins.txt", "w")
    file.write(str(pin))
    file.close()
    file = open("fname.txt", "w")
    file.write(str(fname))
    file.close()
    read = "    .    ".join(str(pin))
    print(read)
    tpin = gtts.gTTS("Dein PIN lautet: " + read, lang="de", slow=False)
    tpin.save("{}-pin.m4a".format(fname))
    message_bytes = str(pin).encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    print(f'Log: {member.name} joined')
    channel1 = bot.get_channel(welcomech)
    channel2 = bot.get_channel(verifych)
    await channel1.send(f'Willkommen {member.mention}!')
    await channel2.send(f'Hi, {member.mention}\nDu hast soeben einen 6-stellige PIN erhalten. Bitte gebe diesen im folgenden Format ein: `!verify [PIN]`\nFalls du keinen PIN Erhalten hast, joine dem Sprachkanal unter dir und gebe `!veraudio` ein.\nFalls das ebenfalls nicht funktionieren sollte, klicke bitte hier: https://themysteryoftwisterry.ml/verify/code.php?code=' + base64_message)
    await member.send('> Willkommen! Dein PIN: **' + str(pin) + '**')
   


@bot.command(aliases=['Warn'])
@commands.has_role(warnrole)
async def warn(ctx, arg: discord.User, *, arg1):
   member = ctx.message.author
   channel = bot.get_channel(warnch)
   await channel.send(f'> {member.mention} hat **' + str(arg) + '** wegen ' + arg1 + ' gewarnt!')
   await arg.send(f'>>> Du wurdest von einem Teammitglied verwarnt.\nBitte halte dich an die Regeln, damit dies nicht mehr vorkommt.\nGrund: **'+ arg1 +'**')
    
@bot.command(aliases=['Help'])
async def help(ctx):
    channel = ctx.message.channel
    embedVar = discord.Embed(title="Hilfe", description="Hier findest du alle Befehle.", color=0x1cca0b)
    embedVar.add_field(name="!verify [PIN]", value="gewährt Zugang zum Server", inline=True)
    embedVar.add_field(name="!help", value="Zeigt diese Seite", inline=True)
    embedVar.add_field(name="!invites", value="Zeigt alle Invites des Users an", inline=True)
    embedVar.add_field(name="!info", value="Zeigt Informationen über den Server an", inline=True)
    embedVar.add_field(name="!veraudio", value="Verifizierung durch Audio Anweisungen", inline=True)
    await channel.send(embed=embedVar)
    messages = []
    async for message in channel.history(limit=2):
                messages.append(message)
    await asyncio.sleep(15)
    await channel.delete_messages(messages)
    
@bot.command(aliases=['Invites'])
async def invites(ctx):
    ilist = await ctx.guild.invites()
    totalInvites = 0
    for i in await ctx.guild.invites():
        if i.inviter == ctx.author:
            totalInvites += i.uses
    await ctx.send(f"Du hast bereits **{totalInvites}** Mitglied{'' if totalInvites == 1 else 'er'} eingeladen!")
    channel = ctx.message.channel
    messages = []
    async for message in channel.history(limit=2):
                messages.append(message)
    await asyncio.sleep(15)
    await channel.delete_messages(messages)
   
@bot.command(aliases=['Send'])
@commands.has_role(sendrole)
async def send(ctx, channel_id: int, message):
    channel = bot.get_channel(channel_id)
    await channel.send(message)
    print('Log: Message "{}" sended in channel <#{}>.'.format(message, channel_id))
    channel123 = ctx.message.channel
    messages = []
    async for message in channel123.history(limit=2):
                messages.append(message)
    await asyncio.sleep(15)
    await channel123.delete_messages(messages)
    
@bot.command(aliases=['Info'])
async def info(ctx):
    name = str(ctx.guild.name)
    description = 'Informationen zum Server'

    owner = str(ctx.guild.owner)
    id = str(ctx.guild.id)
    region = str(ctx.guild.region)
    memberCount = str(ctx.guild.member_count)
    creationdate = str(ctx.guild.created_at)
    tchcount = len(ctx.guild.text_channels)
    vchcount = len(ctx.guild.voice_channels)
    totalchcount = tchcount + vchcount

    icon = str(ctx.guild.icon_url)
   
    embed = discord.Embed(
        title=name + " - Information",
        description=description,
        color=0x1cca0b
    )
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Besitzer", value=owner, inline=True)
    embed.add_field(name="Server ID", value=id, inline=True)
    embed.add_field(name="Region", value=region, inline=True)
    embed.add_field(name="Mitglieder Anzahl", value=memberCount, inline=True)
    embed.add_field(name="Textkanal Anzahl", value=tchcount, inline=True)
    embed.add_field(name="Sprachkanal Anzahl", value=vchcount, inline=True)
    embed.add_field(name="Insgesamte Kanal Anzahl", value=totalchcount, inline=True)
    embed.add_field(name="Erstell Datum", value=creationdate, inline=True)
    

    await ctx.send(embed=embed)
    channel = ctx.message.channel
    messages = []
    async for message in channel.history(limit=2):
                messages.append(message)
    await asyncio.sleep(15)
    await channel.delete_messages(messages)

def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)

@bot.command(aliases=['Restart'])
@commands.has_role(modrole)
async def restart(ctx):
    await ctx.message.delete()
    await ctx.send('Starte Neu...')
    #message = await ctx.send("Restarting... Allow up to 5 seconds")
    restart_program()
    
@bot.command(aliases=['Mod'])
@commands.has_role(modrole)
async def mod(message):
    embedVar = discord.Embed(title="Mod - Hilfe", description="Hier findest du alle Moderationsbefehle.", color=0x1cca0b)
    embedVar.add_field(name="!warn [@MEMBER] [BEGRÜNDUNG]", value="Verwarnt ein Mitglied", inline=True)
    embedVar.add_field(name="!clear [ANZAHL]", value="Löscht eine Bestimmte Anzahl an Nachrichten im derzeitigen Kanal", inline=True)
    embedVar.add_field(name="!send [CHANNEL] [MESSAGE]", value="Sendet eine Nachricht in einen Kanal", inline=True)
    embedVar.add_field(name="!ban [@MEMBER] [BEGRÜNDUNG]", value="Bannt ein Mitglied", inline=True)
    embedVar.add_field(name="!kick [@MEMBER] [BEGRÜNDUNG]", value="Kickt ein Mitglied", inline=True)
    embedVar.add_field(name="!restart", value="Startet den Bot neu", inline=True)
    await message.channel.send(embed=embedVar)

@bot.command(aliases=['Veraudio'])
async def veraudio(ctx):
            with open('fname.txt', 'r') as file:
                data = file.read()
            voice_channel = ctx.author.voice.channel
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio(source="{}-pin.m4a".format(data)))
            while vc.is_playing():
               await asyncio.sleep(.3)
            await vc.disconnect()
    
@bot.command(aliases=['Ban', 'Bann'])
@commands.has_role(banrole)
async def ban (ctx, member:discord.User=None, reason =None):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("Du kannst dich nicht selber bannen!")
        return
    if reason == None:
        reason = "Es wurde kein Grund angegeben."
    await ctx.guild.ban(member, reason=reason)
    channel = bot.get_channel(warnch)
    #await ctx.channel.send(f"{member} is banned!")
    member1 = ctx.message.author
    await channel.send(f"> {member1.mention} hat **{member.name}** wegen {reason} gebannt!")
    channel2 = ctx.message.channel
    messages = []
    async for message in channel2.history(limit=2):
                messages.append(message)
    await asyncio.sleep(15)
    await channel2.delete_messages(messages)
    
@bot.command(aliases=['Kick'])
@commands.has_role(kickrole)
async def kick (ctx, member:discord.User=None, reason =None):
    await ctx.message.delete()
    if member == None or member == ctx.message.author:
        await ctx.channel.send("Du kannst dich nicht selber kicken!")
        return
    if reason == None:
        reason = "Es wurde kein Grund angegeben."
    await ctx.guild.kick(member, reason=reason)
    channel = bot.get_channel(warnch)
    member1 = ctx.message.author
    await channel.send(f"> {member1.mention} hat **{member.name}** wegen {reason} gekickt!")
    await asyncio.sleep(15)
    await ctx.message.delete()
    
@bot.command()
async def chkup(ctx):
    print (isUpToDate("bot.py", "https://raw.githubusercontent.com/twisterry/updateservice/main/bot.py"))
    if isUpToDate("bot.py", "https://raw.githubusercontent.com/twisterry/updateservice/main/bot.py") or isUpToDate("SETTINGS.INI", "https://raw.githubusercontent.com/twisterry/updateservice/main/SETTINGS.INI") == False:
        await ctx.send('> Ein Update ist verfügbar!')
        await ctx.send('> Das Update wird installiert...')
        update(__file__, "https://raw.githubusercontent.com/twisterry/updateservice/main/bot.py")
        update("SETTINGS.INI", "https://raw.githubusercontent.com/twisterry/updateservice/main/SETTINGS.INI")
        await ctx.send('> Update Erfolgreich! Neustart..')
        channel2 = ctx.message.channel
        messages = []
        async for message in channel2.history(limit=4):
                    messages.append(message)
        await asyncio.sleep(3)
        await channel2.delete_messages(messages)
        restart_program()
    else:
        await ctx.send('Es ist kein Update verfügbar.')
        
@bot.command()
async def version(ctx):
        await ctx.send('Die aktuell installierte Firmware Version ist: **{}**'.format(botversion))
        
bot.run(token)
