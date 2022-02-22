import asyncio
import datetime
import discord
from discord.ext import commands
import config
import api_request
from datetime import date, timedelta, datetime


PREFIX = "!"


bot = commands.Bot(command_prefix=PREFIX)
bot.remove_command('help')


async def auto_delete_message(message):
    i = True

    while i == True:
        await asyncio.sleep(1)
        i = False
        await message.delete()


async def create_auto_deleted_message(message):
    loop = asyncio.get_event_loop()
    loop.create_task(auto_delete_message(message))


@bot.command()
async def get_pp(ctx):
    content = ctx.message.content[len(f"{PREFIX}get_pp "):].split(' ')
    users = []
    for i in content:
        users.append(await bot.fetch_user(i))
    await ctx.message.delete()
    if (not users):
        message = await ctx.channel.send("Requested user wasn't found")
        await create_auto_deleted_message(message)
        return
    for user in users:
        await ctx.channel.send(user.avatar_url)



@bot.command()
async def get_banner(ctx):
    content = ctx.message.content[len(f"{PREFIX}get_banner "):].split(' ')
    users = []
    for i in content:
        users.append(await bot.fetch_user(i))
    await ctx.message.delete()
    if (not users):
        message = await ctx.channel.send("Requested user wasn't found")
        await create_auto_deleted_message(message)
        return
    for user in users:
        req = await bot.http.request(discord.http.Route("GET", "/users/{uid}", uid = user.id))
        banner_id = req["banner"]
        if banner_id:
            banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}?size=1024"
            await ctx.channel.send(banner_url)


@bot.command()
async def get_tomorrow(ctx=None):
    tomorrow_date = date.today() + timedelta(days=1)
    formatted_date = tomorrow_date.strftime('%d/%m/%Y')
    calendar = api_request.api_call_day(start=tomorrow_date, end=tomorrow_date)
    nbr_of_entry = len(calendar)
    channel = await bot.fetch_channel(924752159743029279)
    embed = discord.Embed(colour=discord.Colour.blue())

    embed.set_author(name=f"{formatted_date}\n")
    if nbr_of_entry == 0:
        embed.add_field(name="Rien de prévu", value=':)')
        await channel.send(embed=embed)
        return
    while nbr_of_entry > 0:
        start = calendar[nbr_of_entry - 1]["start"]
        end = calendar[nbr_of_entry - 1]["end"]
        hour = f"{start[10:]} -> {end[10:]}"
        titlemodule = calendar[nbr_of_entry - 1]["titlemodule"]
        acti_title = calendar[nbr_of_entry - 1]["acti_title"]
        try:
            room = calendar[nbr_of_entry - 1]['room']['code'][len('FR/PAR/'):]
        except:
            room = "no entry for room"
        activity = f"{titlemodule}\n{acti_title}\n{room.replace('/', ' ').replace('-', '/')}"
        embed.add_field(name=hour, value=activity, inline=False)
        nbr_of_entry -= 1
    await channel.send("<@222008900025581568>")
    await channel.send(embed=embed)
    if ctx:
        await ctx.message.delete()


@bot.command(name="get_day")
async def get_day_from_date(ctx):
    content = ctx.message.content[len(f"{PREFIX}get_day "):].split("/")
    targeted_date = datetime(day=int(content[0]), month=int(content[1]), year=int(content[2]))
    formatted_date = targeted_date.strftime('%d/%m/%Y')
    calendar = api_request.api_call_day(start=targeted_date.strftime('%Y-%m-%d'), end=targeted_date.strftime('%Y-%m-%d'))
    nbr_of_entry = len(calendar)
    channel = await bot.fetch_channel(924752159743029279)
    embed = discord.Embed(colour=discord.Colour.blue())

    embed.set_author(name=f"{formatted_date}\n")
    if nbr_of_entry == 0:
        embed.add_field(name="Rien de prévu", value=':)')
        await channel.send(embed=embed)
        return
    while nbr_of_entry > 0:
        start = calendar[nbr_of_entry - 1]["start"]
        end = calendar[nbr_of_entry - 1]["end"]
        hour = f"{start[10:]} -> {end[10:]}"
        titlemodule = calendar[nbr_of_entry - 1]["titlemodule"]
        acti_title = calendar[nbr_of_entry - 1]["acti_title"]
        try:
            room = calendar[nbr_of_entry - 1]['room']['code'][len('FR/PAR/'):]
        except:
            room = "no entry for room"        
        activity = f"{titlemodule}\n{acti_title}\n{room.replace('/', ' ').replace('-', '/')}"
        embed.add_field(name=hour, value=activity, inline=False)
        nbr_of_entry -= 1
    await ctx.reply(embed=embed)


#@get_day_from_date.error
#async def get_day_from_date_error(ctx, error):
#    await ctx.reply(error)



@bot.command()
async def help(ctx):
    embed = discord.Embed(colour=discord.Colour.blue())
    
    embed.set_author(name="Help\n")
    embed.add_field(name=f"{PREFIX}get_pp *id id id*...", value="Send pps of asked discord ids", inline=False)
    embed.add_field(name=f"{PREFIX}get_banner *id id id*...", value="Send banners of asked discord ids", inline=False)
    embed.add_field(name=f"{PREFIX}get_tomorrow", value="Send tomorroy's schedule", inline=False)
    embed.add_field(name=f"{PREFIX}get_day dd/mm/yyyy", value="Send asked day schedule", inline=False)

    await ctx.reply("Look your DM")
    await ctx.author.send(embed=embed)

async def set_interval(fct =get_tomorrow):
    while True:
        tomorrow_date = date.today() + timedelta(days=1)
        targeted_date = datetime(year=tomorrow_date.year, month=tomorrow_date.month, day=tomorrow_date.day, hour=17)
        substraction_result = targeted_date - datetime.now()
        await asyncio.sleep(substraction_result.total_seconds())
        await fct()


async def create_loop():
    loop = asyncio.get_event_loop()
    loop.create_task(set_interval())


@bot.event
async def on_ready():
    print('bot is ready !')
    await create_loop()


bot.run(config.TOKEN)
