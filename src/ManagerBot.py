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


#@nickname.error
#async def nickname_error(ctx, error):
#  await ctx.send("Error in the nickname command! The  format for the nickname command is| .nickname {@user} {nickname}|.")

####################################################################################################################

#ADMINISTRATION COMMANDS
@bot.command()
async def ban(ctx, member : discord.Member, reason=None):
    if reason == None:
        await ctx.send(f"Please provide a reason for the ban, {ctx.author.mention}!")
    else:
        banMessage = f"This member has been banned from ths server for {reason}."
        await member.send(banMessage)
        await member.ban(reason=reason)

@bot.command()
@commands.has_permissions(administrator = True)
async def unban(ctx, *, member: discord.Member, description="Unbans a user."):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.member

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(member)
            await ctx.send(f'Unbanned {member}')
            return

@commands.is_owner() #make sure no one else uses it
@bot.command()
async def stop_bot(ctx):
    exit()
####################################################################################################################
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong!\nLatency: `{round(bot.latency * 1000)} ms`')


@bot.command()
async def invite(ctx):
    await ctx.send(
        'Here is the invite link: https://discord.com/api/oauth2/authorize?client_id=769306404720214028&permissions=0'
        '&scope=bot')

@bot.command()
async def softban(ctx, member: discord.Member, reason=None, description = "Clears out all messages from a user by banning and unbanning them."):
    if reason == None:
        await ctx.send(f'Please provide a reason for the softban, {user.mention}!')
        softbanMessage = f'This member has been banned from this server for {reason}.'
    await member.send(softbanMessage)
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.member

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(member)
            await ctx.send(f'Unbanned {member}')
            return





@bot.command(pass_context=True)
async def nickname(ctx, member: discord.Member, nick):
    if ctx.message.author.guild_permissions.administrator:
        await member.edit(nick=nick)
        await ctx.send(f'Nickname was changed for {member.mention}.')
    else:
        await ctx.send("You don't have the permission to do this!")

@bot.command(pass_context=True)
async def blacklist(ctx, member: discord.Member, *, reason=""):
  if ctx.message.author.guild_permissions.administrator:
    role = get(member.server.roles, name="Manager Bot Blacklist")
    await bot.add_roles(member, role)
    await ctx.send(member + ' was blacklisted from using Manager Bot on this server.')
  else:
    await ctx.send("You don't have the permission to do this!")

  if role == None:
      await ctx.guild.create_role("Manager Bot Blacklist")

@bot.command()
async def mute(ctx, member: discord.Member, pass_context=True):
    await member.edit(mute=True)

@bot.command()
async def poll(ctx, question, option1=None, option2=None):
    await ctx.channel.purge(limit=1)
    message = await ctx.send(f"```New poll: \n{question}```\n**✅ = Yes**\n**❌ = No**")
    await message.add_reaction('✅')
    await message.add_reaction('❌')
    await ctx.send("Done!")


@bot.command()
async def diceroll(ctx):
    faces = ['1', '2', '3', '4', '5', '6']
    await ctx.send(random.choice(faces))

@bot.command()
async def mentionmember(ctx, member: discord.Member, aliases=['mm', 'mention']):
    await ctx.send(f"That member's name is {member.mention}")
    if member == None:
        await ctx.send("Please provide someone to mention! ")




bot.run('TOKEN HERE')
