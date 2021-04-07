import random
import time
import asyncio
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
        await ctx.guild.ban(member)
        await member.send(banMessage)


@bot.command()
@commands.has_permissions(administrator = True)
async def unban(ctx, *, member: discord.Member):
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

@bot.command()
async def clear(ctx, messageamount, limit=1):
    await ctx.channel.purge(limit=int(messageamount)+1)
    await ctx.send(f"{messageamount}messages cleared by {ctx.message.author.mention}.")

@bot.command()
async def mute(ctx, member: discord.Member, pass_context=True):
    await member.edit(mute=True)

@bot.command()
async def warn(ctx, member: discord.Member, warnmsg):
    user = bot.get_user(member.id)
    await user.send(f"{ctx.message.author} has warned you for {warnmsg}.")
####################################################################################################################

# HELP SECTION/HELP RELATED COMMANDS
@bot.remove_command("help")

@bot.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title='Help', description='Use .help <commandname> for help on specific commands!')
    em.add_field(name='Moderation', value='ban, unban, softban, mute, clear, warn')
    em.add_field(name='Utilities', value='ping, invite, nickname, poll')
    em.add_field(name='Fun', value='mentionmember, kill, diceroll, reverse, fortune')

    await ctx.send(embed=em)
'''
@help.command()
async def ban(ctx):
    em = discord.Embed(title='Ban', description='This command bans a user from a server.')
    em.add_field(name='Usage: .ban <@username> <reason>')

@help.command()
async def unban(ctx):
    em = discord.Embed(title='Unban', description='This command unbans a user from a server.')
    em.add_field(name='Usage: .unban <@username> <reason>')

@help.command()
async def softban(ctx):
    em = discord.Embed(title='Softban', description='The softban command is currently being worked on, but will ban and immediately unban a user.')
    em.add_field(name='Usage: COMMAND STILL BEING WORKED ON')

@help.command()
async def mute(ctx):
    em = discord.Embed(title='Mute', description='The mute command mutes a user so they can\'t send a message in any channel.')
    em.add_field(name='Usage: .mute <@username>')

@help.command()
async def clear(ctx):
    em = discord.Embed(title='Clear', description='Clears a certain amount of messsages from the channel the command was sent in. ')
    em.add_field(name='Usage: .clear <amount>')

@help.command()
async def ping(ctx):
    em = discord.Embed(title='Ping', description='Sends the ping of the bot.')
    em.add_field(name='Usage: .ping')

@help.command()
async def invite(ctx):
    em = discord.Embed(title='Invite', description='Sends the invite link for this bot. The link can be used to invite the bot to other servers.')
    em.add_field(name='Usage: .invite')

@help.command()
async def nickname(ctx):
    em = discord.Embed(title='Nickname', description='Changes the nickname of a user.')
    em.add_field(name='Usage: .nickname <@username> <newnickname>')

@help.command()
async def poll(ctx):
    em = discord.Embed(title='Poll', description='Creates a poll in the channel the command was sent in.')
    em.add_field(name='Usage: .poll <question> <option1> <option2>')

@help.command()
async def mentionmember(ctx):
    em = discord.Embed(title='Mention (mentionmember)', description='This command bans a user from a server.')
    em.add_field(name='Usage: .mentionmember <member>')

@help.command()
async def kill(ctx):
    em = discord.Embed(title='Kill', description='Sends a kill message to targetted user >:)')
    em.add_field(name='Usage: .kill <username>')

@help.command()
async def diceroll(ctx):
    em = discord.Embed(title='Diceroll', description='Rolls a die.')
    em.add_field(name='Usage: .diceroll')
'''
####################################################################################################################
# CURRENCY RELATED COMMANDS
#users=
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
async def softban(ctx, member: discord.Member, duration: int):
    await ctx.guild.ban(member)
    await time.sleep(duration)
    await ctx.guild.unban(member)

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
async def kill(ctx, member: discord.Member):
    kmethod=['discombobulated','sliced', 'hit','slapped','exploded', 'decapitated', 'yeeted', 'deleted']
    kweapon=['sword', 'bomb', 'plane', 'bowl of milk', 'bread', 'baguette', 'car', 'nuke', 'pig', 'monkey', 'rocket launcher']
    await ctx.send(f"{member.mention} was {random.choice(kmethod)} by a {random.choice(kweapon)} sent by {ctx.message.author.mention}")


@bot.command()
async def poll(ctx, question, option1=None, option2=None):
    await ctx.channel.purge(limit=1)
    message = await ctx.send(f"```New poll: \n{question}```\n**✅ = Yes**\n**❌ = No**")
    await message.add_reaction('✅')
    await message.add_reaction('❌')
    await ctx.send("Done!")

@bot.command()
async def reverse(ctx, message):
    await ctx.send(str(message)[::-1])
    if message == None:
        await ctx.send("You must provide a string to reverse!")

@bot.command()
async def diceroll(ctx):
    faces = ['1', '2', '3', '4', '5', '6']
    await ctx.send(random.choice(faces))

@bot.command()
async def mentionmember(ctx, member: discord.Member, aliases=['mm', 'mention']):
    await ctx.send(f"That member's name is {member.mention}")
    if member == None:
        await ctx.send("Please provide someone to mention! ")

@bot.command()
async def fortune(ctx):
    day = ['In a while from now,', 'Later,', 'In some time,', 'Soon,', 'When the royal pig army takes over Scandanavia,']
    amount = [' a lot', ' an abundance of', ' a little bit of', ' a hundred thousand', ' some']
    item = [' of money', ' nukes', ' monkeys', ' pigs', ' cars', ' planes', ' explosions', ' strange noises']
    await ctx.send(f"{random.choice(day)} you will recieve{random.choice(amount)}{random.choice(item)}.")

@bot.command()
async def hack(ctx, member: discord.Member):
    waittime = [0.2, 0.3, 1, 0.5, 0.6, 0.4, 0.7, 0.01]
    msg = await ctx.send(f"Hacking {member} now.")
    await msg.edit(content="1%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="2%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="5%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="11%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="13%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="ERROR: RAN INTO 2FA, BRUTE FORCING NOW...")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="15%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="20%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="30%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="41%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="48%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="61%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="75%")
    await asyncio.sleep(random.choice(waittime))
    await msg.edit(content="STEALING AND REPOSTING MEMES NOW...")
    await asyncio.sleep(random.choice(waittime))
    await ctx.send("SUCCESSFULLY HACKED!")

@bot.command()
async def coinflip(ctx):
    headstails=['heads', 'tails']
    await ctx.send(f"The result is {random.choice(headstails)}!")

@bot.command()
async def guess(self, ctx):
    numbers=random.randint(1,10)
    await ctx.send('I have chosen a number from 1 to 10. Try to guess my number!')
    try:
        guess = await self.wait_for('message', check=is_correct, timeout=10.0)
    except asyncio.TimeoutError:
        ctx.send(f"10 seconds are over! The answer was {numbers}")


bot.run('TOKEN HERE')
