import random
import time
import asyncio
import discord
from discord.ext import commands
import os
import json
import pickle
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

@commands.is_owner() # Makes sure no one else uses it
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
    em = discord.Embed(title='Help', description='A list of commands!')
    em.add_field(name='Moderation', value='ban, unban, softban, mute, clear, warn')
    em.add_field(name='Utilities', value='ping, invite, nickname, poll')
    em.add_field(name='Fun', value='mentionmember, kill, diceroll, reverse, fortune, guess')
    em.add_field(name='Currency', value='beg, bal, deposit, withdraw, gamble, guess')

    await ctx.send(embed=em)
'''
@help.command()
async def ban(ctx):
    em = discord.Embed(title='Ban', description='This command bans a user from a server.')
    em.add_field(name='Usage: .ban <@username> <reason>')
    await ctx.send(em)

@help.command()
async def unban(ctx):
    em = discord.Embed(title='Unban', description='This command unbans a user from a server.')
    em.add_field(name='Usage: .unban <@username> <reason>')
    await ctx.send(em)

@help.command()
async def softban(ctx):
    em = discord.Embed(title='Softban', description='The softban command is currently being worked on, but will ban and immediately unban a user.')
    em.add_field(name='Usage: COMMAND STILL BEING WORKED ON')
    await ctx.send(em)

@help.command()
async def mute(ctx):
    em = discord.Embed(title='Mute', description='The mute command mutes a user so they can\'t send a message in any channel.')
    em.add_field(name='Usage: .mute <@username>')
    await ctx.send(em)

@help.command()
async def clear(ctx):
    em = discord.Embed(title='Clear', description='Clears a certain amount of messsages from the channel the command was sent in. ')
    em.add_field(name='Usage: .clear <amount>')
    await ctx.send(em)

@help.command()
async def ping(ctx):
    em = discord.Embed(title='Ping', description='Sends the ping of the bot.')
    em.add_field(name='Usage: .ping')
    await ctx.send(em)

@help.command()
async def invite(ctx):
    em = discord.Embed(title='Invite', description='Sends the invite link for this bot. The link can be used to invite the bot to other servers.')
    em.add_field(name='Usage: .invite')
    await ctx.send(em)

@help.command()
async def nickname(ctx):
    em = discord.Embed(title='Nickname', description='Changes the nickname of a user.')
    em.add_field(name='Usage: .nickname <@username> <newnickname>')
    await ctx.send(em)

@help.command()
async def poll(ctx):
    em = discord.Embed(title='Poll', description='Creates a poll in the channel the command was sent in.')
    em.add_field(name='Usage: .poll <question> <option1> <option2>')
    await ctx.send(em)

@help.command()
async def mentionmember(ctx):
    em = discord.Embed(title='Mention (mentionmember)', description='This command bans a user from a server.')
    em.add_field(name='Usage: .mentionmember <member>')
    await ctx.send(em)

@help.command()
async def kill(ctx):
    em = discord.Embed(title='Kill', description='Sends a kill message to targetted user >:)')
    em.add_field(name='Usage: .kill <username>')
    await ctx.send(em)

@help.command()
async def diceroll(ctx):
    em = discord.Embed(title='Diceroll', description='Rolls a die.')
    em.add_field(name='Usage: .diceroll')
    await ctx.send(em)
'''
####################################################################################################################
# CURRENCY RELATED COMMANDS

data_filename = "data.pickle"

class Data:
    def __init__(self, wallet, bank):
        self.wallet = wallet
        self.bank = bank


#Commands
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def beg(ctx):
    member_data = load_member_data(ctx.message.author.id)
    gain_amt = random.randint(0,201)
    member_data.wallet += gain_amt
    em = discord.Embed(title = 'Beg', description = f'You earned {gain_amt} coins!, You can use this command again in 2 seconds.')
    await ctx.send(embed=em)

    save_member_data(ctx.message.author.id, member_data)

@bot.command()
async def bal(ctx):
    member_data = load_member_data(ctx.message.author.id)

    em = discord.Embed(title=f"Balance of {ctx.message.author}")
    em.add_field(name="Wallet", value=str(member_data.wallet))
    em.add_field(name="Bank", value=str(member_data.bank))
    await ctx.send(embed = em)

@beg.error
async def beg_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"Hey, I need a break too!",description=f"Try again in {error.retry_after:.2f} sseconds.")
        await ctx.send(embed=em)

    await message.channel.send(embed=em)

@bot.command()
async def deposit(ctx, deposit_amt):
    member_data = load_member_data(ctx.message.author.id)

    deposit_amt = int(deposit_amt)

    if deposit_amt == None:
        em = discord.Embed(title="Error!", description = "Please provide an amount to deposit!")
        await ctx.send(embed = em)

    elif deposit_amt <0:
        em = discord.Embed(title="Error!", description = "Please provide a positive amount to deposit!")
        await ctx.send(embed = em)

    elif deposit_amt > member_data.wallet:
        em = discord.Embed(title="Error!", description = "The value you are depositing is more than what you have in your wallet!")
        await ctx.send(embed = em)

    else:
        member_data.bank += deposit_amt
        member_data.wallet -= deposit_amt
        save_member_data(ctx.message.author.id, member_data)
        await ctx.send(f"Deposited {deposit_amt} coins!")

@bot.command()
async def withdraw(ctx, withdraw_amt):
    member_data = load_member_data(ctx.message.author.id)

    withdraw_amt = int(withdraw_amt)


    if withdraw_amt == None:
        em = discord.Embed(title="Error!", description = "Please provide an amount to withdraw!")
        await ctx.send(embed = em)

    elif withdraw_amt <0:
        em = discord.Embed(title="Error!", description = "Please provide a positive amount to withdraw!")
        await ctx.send(embed = em)

    elif withdraw_amt > member_data.bank:
        em = discord.Embed(title="Error!", description = "The value you are withdrawing is more than what you have in your bank!")
        await ctx.send(embed = em)

    else:
        member_data.bank -= withdraw_amt
        member_data.wallet += withdraw_amt
        save_member_data(ctx.message.author.id, member_data)
        await ctx.send(f"Withdrew {withdraw_amt} coins!")


@bot.command()
async def gamble(ctx, gamble_amt):

    member_data = load_member_data(ctx.message.author.id)

    gamble_amt = int(gamble_amt)

    if gamble_amt == None or gamble_amt < 0:
        em = discord.Embed(title="Error!", description = "Please provide a valid amount to gamble!")
        await ctx.send(embed = em)

    elif gamble_amt < 100:
        em = discord.Embed(title="Error!", description = "Please gamble at least 100 coins!")
        await ctx.send(embed = em)

    elif gamble_amt > member_data.wallet:
        em = discord.Embed(title="Error!", description = "The value you are gambling is more than what you have in your wallet!")
        await ctx.send(embed = em)

    else:
        userchance = random.randint(0,7)
        botchance = random.randint(0,7)

        if userchance > botchance:
            member_data.wallet += gamble_amt
            save_member_data(ctx.message.author.id, member_data)
            em = discord.Embed(title="You Won!", description = f"You gained {gamble_amt} credits! ")
            await ctx.send(embed = em)

        elif botchance > userchance:
            member_data.wallet -= gamble_amt
            save_member_data(ctx.message.author.id, member_data)
            em = discord.Embed(title="You Lost :(", description = f"You lost {gamble_amt} credits. ")
            await ctx.send(embed = em)

        else:
            em = discord.Embed(title="Tie!", description = f"You didn't gain or lose anything. ")
            await ctx.send(embed = em)


@bot.command()
@commands.cooldown(1, 20, commands.BucketType.user)
async def guess(ctx):
    member_data = load_member_data(ctx.message.author.id)

    number = random.randint(1,10)
    print(number)
    number = str(number)
    await ctx.send("I have chosen a number from 1-10! Try to guess my number. You have three guesses!")
    guess = await bot.wait_for('message')
    guess = guess.content


    if guess == number:
        member_data.wallet += 50
        save_member_data(ctx.message.author.id, member_data)
        await ctx.send("You got it! You have recieved 50 credits!")

    elif guess != number:
        em = discord.Embed(title="That wasn't it!", description = "Try again in 20 seconds")
        await ctx.send(embed = em)

@guess.error
async def guess_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"Hey, I need a break too!",description=f"Try again in {error.retry_after:.2f} sseconds.")
        await ctx.send(embed=em)

@commands.is_owner()
@bot.command()
async def gimmemoney(ctx, give_amt):
    if ctx.message.author.id == 725412711495762001:
        member_data = load_member_data(ctx.message.author.id)
        member_data.wallet += int(give_amt)
        save_member_data(ctx.message.author.id, member_data)
        await ctx.send(f"Gave {give_amt} :hearts:")


#Functions
def load_data():
    if os.path.isfile(data_filename):
        with open(data_filename, "rb") as file:
            return pickle.load(file)
    else:
        return dict()

def load_member_data(member_ID):
    data = load_data()

    if member_ID not in data:
        return Data(0, 0)

    return data[member_ID]

def save_member_data(member_ID, member_data):
    data = load_data()

    data[member_ID] = member_data

    with open(data_filename, "wb") as file:
        pickle.dump(data, file)

####################################################################################################################


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong!\nLatency: `{round(bot.latency * 1000)} ms`')


@bot.command()
async def invite(ctx):
    await ctx.send(
        'Here is the invite link: https://discord.com/api/oauth2/authorize?_id=769306404720214028&permissions=0'
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
    await ctx.send(f"Successfully hacked {member.mention}!")

@bot.command()
async def coinflip(ctx):
    headstails=['heads', 'tails']
    await ctx.send(f"The result is {random.choice(headstails)}!")




bot.run('TOKEN HERE')
