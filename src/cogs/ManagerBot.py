import random
import time
import asyncio
import discord
from discord.ext import commands, tasks
from itertools import cycle
import os
import json
import pickle
import requests
# Set-up and running process
from discord.ext.commands import bot, check, context


bot = commands.Bot(command_prefix='.')


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,
      activity=discord.Game('Use .help for a list of commands :)'))
    print("The manager is ready to go.")

@bot.remove_command("help")

@bot.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title='Help', description='A list of commands!')
    em.add_field(name='Moderation', value='ban, unban, softban, mute, clear, warn')
    em.add_field(name='Utilities', value='ping, invite, nickname, poll')
    em.add_field(name='Fun', value='mentionmember, kill, diceroll, reverse, fortune, guess, bitconi')
    em.add_field(name='Currency', value='beg, bal, deposit, withdraw, gamble, guess, daily, shop, buy')

    await ctx.send(embed=em)
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

def converttohr(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

####################################################################################################################
# CURRENCY RELATED COMMANDS

data_filename = "data.pickle"
inventory_filename = "inventory.pickle"

class Data:
    def __init__(self, wallet, bank):
        self.wallet = wallet
        self.bank = bank

class invData:
    def __init__(self, inventory):
        self.inventory = []


#Commands
@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def beg(ctx):
    member_data = load_member_data(ctx.message.author.id)
    gain_amt = random.randint(0,201)
    member_data.wallet += gain_amt
    em = discord.Embed(title = 'Beg', description = f'You earned {gain_amt} 💵!, You can use this command again in 2 minutes.')
    em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
    await ctx.send(embed=em)

    save_member_data(ctx.message.author.id, member_data)

@bot.command()
async def bal(ctx):
    member_data = load_member_data(ctx.message.author.id)

    em = discord.Embed(title=f"Balance of {ctx.message.author}")
    em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
    em.add_field(name="Wallet", value=str(member_data.wallet))
    em.add_field(name="Bank", value=str(member_data.bank))
    await ctx.send(embed = em)

@beg.error
async def beg_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"Hey, I need a break too!",description=f"Try again in {error.retry_after:.2f} sseconds.")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed=em)

    await message.channel.send(embed=em)

@bot.command()
async def deposit(ctx, deposit_amt):
    member_data = load_member_data(ctx.message.author.id)

    if (deposit_amt) == None:
        em = discord.Embed(title="Error!", description = "Please provide an amount to deposit!")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    elif deposit_amt == "all" or "a":
        presentwallet = member_data.wallet
        member_data.wallet -= member_data.wallet
        member_data.bank += presentwallet
        save_member_data(ctx.message.author.id, member_data)
        em = discord.Embed(title="Deposited all credits into bank", description = f"{presentwallet} 💵 have been deposited.")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    elif int(deposit_amt) <0:
        em = discord.Embed(title="Error!", description = "Please provide a positive amount to deposit!")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    elif int(deposit_amt) > member_data.wallet:
        em = discord.Embed(title="Error!", description = "The value you are depositing is more than what you have in your wallet!")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    elif deposit_amt == "all" or "a":
        member_data.wallet -= member_data.wallet
        member_data.bank += member_data.wallet
        em = discord.Embed(title="Deposited all credits into bank", description = f"{member_data.wallet} 💵 have been deposited.")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    else:
        member_data.bank += int(deposit_amt)
        member_data.wallet -= int(deposit_amt)
        save_member_data(ctx.message.author.id, member_data)
        await ctx.send(f"Deposited {deposit_amt} credits!")

@bot.command()
async def withdraw(ctx, withdraw_amt):
    member_data = load_member_data(ctx.message.author.id)


    if withdraw_amt == None:
        em = discord.Embed(title="Error!", description = "Please provide an amount to withdraw!")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    elif withdraw_amt == "all" or "a":
        presentbank = member_data.bank
        member_data.wallet += member_data.bank
        member_data.bank -= presentbank
        save_member_data(ctx.message.author.id, member_data)
        em = discord.Embed(title="Withdrew all credits from bank!", description = f"{presentbank} 💵 have been withdrawn!.")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    elif int(withdraw_amt) <0:
        em = discord.Embed(title="Error!", description = "Please provide a positive amount to withdraw!")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    elif int(withdraw_amt) > member_data.bank:
        em = discord.Embed(title="Error!", description = "The value you are withdrawing is more than what you have in your bank!")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    else:
        member_data.bank -= int(withdraw_amt)
        member_data.wallet += int(withdraw_amt)
        save_member_data(ctx.message.author.id, member_data)
        await ctx.send(f"Withdrew {withdraw_amt} 💵!")


@bot.command()
async def gamble(ctx, gamble_amt):

    member_data = load_member_data(ctx.message.author.id)

    gamble_amt = int(gamble_amt)

    if gamble_amt == None or gamble_amt < 0:
        em = discord.Embed(title="Error!", description = "Please provide a valid amount to gamble!")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    elif gamble_amt < 100:
        em = discord.Embed(title="Error!", description = "Please gamble at least 100 💵!")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    elif gamble_amt > member_data.wallet:
        em = discord.Embed(title="Error!", description = "The value you are gambling is more than what you have in your wallet!")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    else:
        userchance = random.randint(0,7)
        botchance = random.randint(0,7)

        if userchance > botchance:
            member_data.wallet += gamble_amt
            save_member_data(ctx.message.author.id, member_data)
            em = discord.Embed(title="You Won!", description = f"You gained {gamble_amt} 💵! ")
            em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = em)

        elif botchance > userchance:
            member_data.wallet -= gamble_amt
            save_member_data(ctx.message.author.id, member_data)
            em = discord.Embed(title="You Lost :(", description = f"You lost {gamble_amt} 💵. ")
            em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = em)

        else:
            em = discord.Embed(title="Tie!", description = f"You didn't gain or lose anything. ")
            em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = em)

@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    member_data = load_member_data(ctx.message.author.id)
    member_data.wallet += 1000
    save_member_data(ctx.message.author.id, member_data)
    em = discord.Embed(title = "Daily Claimed!", description = "You got your daily amount of 1000💵!")
    em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
    await ctx.send(embed=em)



@daily.error
async def daily_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"Daily already claimed!",description=f"Try again in {error.retry_after:.2f} seconds.")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed=em)

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
        em = discord.Embed(title="You got it!", description = "You got 50💵.")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

    elif guess != number:
        em = discord.Embed(title="That wasn't it!", description = "Try again in 20 seconds")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = em)

@guess.error
async def guess_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"Hey, I need a break too!",description=f"Try again in {error.retry_after:.2f} seconds.")
        em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed=em)

@commands.is_owner()
@bot.command()
async def gimmemoney(ctx, give_amt):
    if ctx.message.author.id == 725412711495762001:
        member_data = load_member_data(ctx.message.author.id)
        member_data.wallet += int(give_amt)
        save_member_data(ctx.message.author.id, member_data)
        await ctx.send(f"Gave {give_amt} :hearts:")



shoplist = [{"name": "Laptop", "price":1000},
        {"name": "Car", "price":10000},
        {"name": "House", "price":5000000}]

@bot.command()
async def shop(ctx):
    shopem = discord.Embed(title = "Shop")
    for item in shoplist:
        item_name = item["name"]
        price = item["price"]
        shopem.add_field(name = item_name, value = f"{price} 💵")

    await ctx.send(embed = shopem)

'''

@bot.command()
async def buy(ctx, number=1, choice=None):
    member_data = load_member_data(ctx.message.author.id)
    member_data = load_member_inventory(ctx.message.author.id)
    for item in shoplist:
        items = []
        item_name = item["name"]
        price = item["name": choice]["price"]*number
        print(price)
        items.append(item_name)

    if choice not in items:
        await ctx.send("That is not a valid item!")

    elif choice == None:
        await ctx.send("Please specify an item!")

    elif member_data.wallet < price:
        await ctx.send("You do not have enough money to buy that item!")

    else:
        member_data.wallet -= price
        x = number
        while x < 0:
            member_data.inventory.append(choice)
            x = x-1
        save_member_data(ctx.message.author.id, member_data)
        save_member_inventory (ctx.message.author.id, member_data)


@bot.command()
async def inventory(ctx, member: discord.Member=None):
    member_data = load_member_inventory(member.id)
    if member == None:
        member = ctx.message.author
        pass
    em = discord.Embed(title = f"{member}\'s inventory", description = " ")
    for item in member_data.inventory:
        em.add_field(item)
    await ctx.send(embed = em)

'''

@shop.error
async def shop_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        em = discord.Embed(title = "Please enter a valid page number for the shop!", description = "To view the first page, do .shop 1, and to view other pages, \n do .shop #")
        await ctx.send(embed = em)
#Functions for credits
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

#######################################################

def load_inventory():
    if os.path.isfile(inventory_filename):
        with open(inventory_filename, "rb") as file:
            return pickle.load(file)
    else:
        return dict()

def load_member_inventory(member_ID):
    data = load_data()

    if member_ID not in data:
        return Data(0, 0)

    return data[member_ID]

def save_member_inventory(member_ID, member_data):
    data = load_data()

    data[member_ID] = member_data


    with open(inventory_filename, "wb") as file:
        pickle.dump(data, file)



####################################################################################################################


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong!\nLatency: `{round(bot.latency * 1000)} ms`')

@bot.command()
async def bitcoin(ctx):
    response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
    bitContent = response.json()

    chartName = bitContent['chartName']
    symbol = bitContent['bpi']['USD']
    rate = bitContent['bpi']['USD']['rate']

    em = discord.Embed(title=f'{chartName}', description = f'Current Value: {rate}')
    em.set_author(name = ctx.message.author.display_name, icon_url = ctx.message.author.avatar_url)
    em.add_field(name="______", value="[Powered by CoinDesk.](https://www.coindesk.com/price/bitcoin)")
    await ctx.send(embed = em)

@bot.command()
async def invite(ctx):
    await ctx.send(
        'Here is the invite link: https://discord.com/api/oauth2/authorize?_id=769306404720214028&permissions=0'
        '&scope=bot')

@bot.command()
async def softban(ctx, member: discord.Member):
    await ctx.guild.ban(member)
    await time.sleep(1)
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


bot.load_extension("tickets")

bot.run('TOKEN HERE')
