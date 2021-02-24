import random
import time

import discord
from discord.ext import commands
# Set-up and running process
from discord.ext.commands import bot, check, context

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    await client.change_presence(status=discord.Status.online,
      activity=discord.Game('For help, use .help :)'))
    print("The manager is ready to go.")


# End of set-up

@bot.event
async def on_member_join(member):
    f = open('logs.txt', 'a')
    print(f'{member} has joined a server. server at time ' + time.time() + '.')
    f.close()


@bot.event
async def on_member_remove(member):
    f = open('logs.txt', 'a')
    print(f'{member} has left a server.')
    f.write(str(member) + ' has left a server at time ' + time.time() + '.')
    f.close()

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.send("There is no such command!")

#@nickname.error
async def nickname_error(ctx, error):
  await ctx.send("Error in the nickname command! The  #format for the nickname command is| .nickname {@user} #{nickname}|.")

####################################################################################################################


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong!\nLatency: `{round(bot.latency * 1000)} ms`')


@bot.command()
async def invite(ctx):
    await ctx.send(
        'Here is the invite link: https://discord.com/api/oauth2/authorize?client_id=769306404720214028&permissions=0'
        '&scope=bot')

#@client.command()
#async def featuredservers(ctx, )

@bot.command(pass_context=True)
async def nickname(ctx, member: discord.Member, nick):
  if ctx.message.author.guild_permissions.administrator:
    await member.edit(nick=nick)
    await ctx.send(f'Nickname was changed for {member.mention}.')

  


@client.command()
async def diceroll(ctx):
    faces = ['1', '2', '3', '4', '5', '6']
    await ctx.send(random.choice(faces))


@client.command()
async def name(ctx):
    await ctx.send("Say a name: ")
    time.sleep(0.1)
    member_name = await bot.wait_for('message', check=check(context.author), timeout=30)
    print(member_name)


client.run('TOKEN HERE')
