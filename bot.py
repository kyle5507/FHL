import asyncio
import os
import discord
import requests

from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient

from helper import extract_element_from_json
from player import Player

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
HUB = os.getenv('FACEIT_HUB')
FACEITAPI = os.getenv('FACEIT_KEY')
SEASON = os.getenv("SEASON")
MONGODB = os.getenv("MONGO")
mapname = ""
losers = ""
winners = ""
players = []

cluster = MongoClient(MONGODB)
db = cluster["FHL"]
collection = db["FHL"]

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Bot Online!")
    bot.loop.create_task(my_task())
    await bot.change_presence(activity=discord.Game(name="Kybrid 10 mans"))


@bot.command(name='match')
async def recmatch(ctx):
    print("Attempting to send recent match..")
    updaterecentmatch()
    await ctx.send(f"Map: {mapname[3:]} \n\nWinners:\n - {winners}\n\nLosers:\n - {losers}")


@bot.command(name='leaderboard')
async def leaderboard(ctx):
    print("Attempting to send leaderboard..")
    updateleaderboard()
    msg = "Leaderboard:\n"
    for player in players:
        msg += (repr(player))
        msg += "\n\n"
    saveMsg("leaderboard", await ctx.send(msg))


def saveMsg(type, msg):
    post = {"type": type,
            "messageID": msg.id,
            "channelID": msg.channel.id}
    if collection.find_one({"type": type}):
        collection.delete_one({"type": type})
    collection.insert_one(post)


async def my_task():
    while True:
        print("Updating leaderboard..")
        post = collection.find_one({"type": "leaderboard"})
        cid = post["channelID"]
        mid = post["messageID"]

        channel = bot.get_channel(cid)
        message = await channel.fetch_message(mid)

        updateleaderboard()
        msg = "Leaderboard:\n"
        for player in players:
            msg += (repr(player))
            msg += "\n\n"
        await message.edit(content=msg)
        await asyncio.sleep(300)


def updateleaderboard():
    global players
    response = requests.get(
        f"https://open.faceit.com/data/v4/leaderboards/hubs/{HUB}/seasons/{SEASON}?offset=0&limit=5",
        headers={'Accept': 'application/json',
                 'Authorization': f"Bearer {FACEITAPI}"})
    jsonresp = response.json()
    nick = extract_element_from_json(jsonresp, ["items", "player", "nickname"])
    skill = extract_element_from_json(jsonresp, ["items", "player", "skill_level"])
    won = extract_element_from_json(jsonresp, ["items", "won"])
    loss = extract_element_from_json(jsonresp, ["items", "lost"])
    pos = extract_element_from_json(jsonresp, ["items", "position"])
    points = extract_element_from_json(jsonresp, ["items", "points"])
    streak = extract_element_from_json(jsonresp, ["items", "current_streak"])
    players.clear()
    for i in range(len(nick)):
        players.append(Player(nick[i], skill[i], won[i], loss[i], streak[i], pos[i], points[i]))


def updaterecentmatch():
    global winners, losers, mapname
    response = requests.get(f"https://open.faceit.com/data/v4/hubs/{HUB}/matches?type=past&offset=0&limit=1",
                            headers={'Accept': 'application/json',
                                     'Authorization': f"Bearer {FACEITAPI}"})
    jsonresp = response.json()
    winner = (extract_element_from_json(jsonresp, ["items", "results", "winner"]))[0]
    if winner == "faction1":
        loser = "faction2"
    else:
        loser = "faction1"
    winners = '\n - '.join(extract_element_from_json(jsonresp, ["items", "teams", f"{winner}", "roster", "nickname"]))
    losers = '\n - '.join(extract_element_from_json(jsonresp, ["items", "teams", f"{loser}", "roster", "nickname"]))
    mapname = extract_element_from_json(jsonresp, ["items", "voting", "map", "pick"])[0][0]


def cleanMarkup(str):
    return str.strip("_").strip("*")


bot.run(TOKEN)
