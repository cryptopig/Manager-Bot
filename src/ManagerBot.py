import random
import time

import discord
from discord.ext import commands
# Set-up and running process
from discord.ext.commands import bot, check, context

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,
      activity=discord.Game('Use .help for a list of commands :)'))
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
async def command_not_found_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.send("There is no such command!")

@bot.event
async def disabled_command_error(ctx, error):
  if isinstance(error, commands.DisabledCommand):
    await ctx.send("This command has been disabled!")

@bot.event
async def bad_argument_error(ctx, error):
  if isinstance(error,commands.BadArgument):
    await ctx.send("Please put the right arguments in the command!")

@bot.event
async def on_message(message):
    if "Manager Bot" in message.content:
        await ctx.send(";)")

@nickname.error
async def nickname_error(ctx, error):
  await ctx.send("Error in the nickname command! The  format for the nickname command is| .nickname {@user} {nickname}|.")

####################################################################################################################

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong!\nLatency: `{round(bot.latency * 1000)} ms`')


@bot.command()
async def invite(ctx):
    await ctx.send(
        'Here is the invite link: https://discord.com/api/oauth2/authorize?client_id=769306404720214028&permissions=0'
        '&scope=bot')


@bot.command(pass_context=True)
async def nickname(ctx, member: discord.Member, nick):
  if ctx.message.author.guild_permissions.administrator:
    await member.edit(nick=nick)
    await ctx.send(f'Nickname was changed for {member.mention}.')
  else:
    await ctx.send("You dont' have the permission to do this!")

@bot.command(pass_context=True)
async def blacklist(ctx, member: discord.Member):
  if ctx.message.author.guild_permissions.administrator:
    role = get(member.server.roles, name="Manager Bot Blacklist")
    await bot.add_roles(member, role)
    await ctx.send(member + ' was blacklisted from using Manager Bot on this server.')
  else:
    await ctx.send("You don't have the permission to do this!")


@bot.command()
async def diceroll(ctx):
    faces = ['1', '2', '3', '4', '5', '6']
    await ctx.send(random.choice(faces))

@bot.command()
async def name(ctx):
    await ctx.send("Say a name: ")
    time.sleep(0.1)
    member_name = await bot.wait_for('message', check=check(context.author), timeout=30)
    print(member_name)


bot.run('TOKEN HERE')
