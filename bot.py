import os
import discord
import requests

from discord.ext import commands, tasks
from dotenv import load_dotenv
from player import Player

from helper import extract_element_from_json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
HUB = os.getenv('FACEIT_HUB')
FACEITAPI = os.getenv('FACEIT_KEY')
SEASON = os.getenv("SEASON")
mapname = ""
losers = ""
winners = ""
players = []
message = discord.Message

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Bot Online!")
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
    await ctx.send(msg)


def updateleaderboard():
    global players
    response = requests.get(
        f"https://open.faceit.com/data/v4/leaderboards/hubs/{HUB}/seasons/{SEASON}?offset=0&limit=5",
        headers={'Accept': 'application/json',
                 'Authorization': f"Bearer {FACEITAPI}"})
    jsonresp = response.json()
    temp = []
    nick = extract_element_from_json(jsonresp, ["items", "player", "nickname"])
    skill = extract_element_from_json(jsonresp, ["items", "player", "skill_level"])
    won = extract_element_from_json(jsonresp, ["items", "won"])
    loss = extract_element_from_json(jsonresp, ["items", "lost"])
    pos = extract_element_from_json(jsonresp, ["items", "position"])
    points = extract_element_from_json(jsonresp, ["items", "points"])
    streak = extract_element_from_json(jsonresp, ["items", "current_streak"])
    for i in range(len(nick)):
        temp.append(Player(nick[i], skill[i], won[i], loss[i], streak[i], pos[i], points[i]))
    players = temp;


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


class MyCog(commands.Cog):
    def __init__(self):
        self.matchcount.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(minutes=15)
    async def printer(self):
        print(self.index)
