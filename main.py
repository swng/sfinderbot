import discord
from copy import deepcopy
from discord.ext import commands
import os
from os import path, listdir, makedirs, remove, environ, rmdir, getcwd
from bs4 import BeautifulSoup
from json import loads
from PIL import Image
import traceback
import io
import math
from py_fumen_util import disassemble, assemble, join, split as fumensplit, mirror as flip
from py_fumen_py import decode as pydecode, encode as pyencode, Field, Page
import requests
from datetime import datetime
import asyncio
import json
import re
from marfungextended import extendPieces
import random
import matplotlib.pyplot as plt
import matplotlib as mpl
import contextlib
from urllib.parse import urlencode
from urllib.request import urlopen
from replit import db
import csv
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from statistics import mean
import sys
import math
import numpy as np
from discord.ext import tasks
from itertools import permutations
from dotenv import load_dotenv
import traceback

load_dotenv()

bot_token = environ["bot_token"]


class sfindercommandtooslow(Exception):
  pass


class commandKilled(Exception):
  pass


newslettergroup = [
  344936089204817930, 601328314203766784, 554411603609518095,
  696811705619054633, 592099842734555174, 395426519331373067,
  461298560416219148, 803050948695556117
]


# Also works for message objects
def bot_admin(ctx):  # i cba to keep copy pasting this

  key = f"bot_admin{ctx.author.id}"
  main_devs = [717451031897833512, 696811705619054633, 186274635220779009, 1187516479051157524] # epic, cringe, swng, kzl
  return key in db.keys() or ctx.author.id in main_devs

# Also works for message objects
def limit_bypass(ctx):
  key = f"limit_bypass{ctx.author.id}"
  return key in db.keys()


cash = []  # [uid:money]


class Command():  # NOTE: DO NOT USE IN DMS
  def __init__(self, ctx):
    self.a_ctx = ctx  # author ctx
    self.pass_bets = []  # [uid:money]
    self.fail_bets = []  # [uid:money]

  async def addBet(ctx, amount, bet):
    if ctx.guild == None or ctx.author.id == a_ctx.author.id:  # if better is author
      await ctx.reply("You can't bet on your own command. Fuck you.")

    if (amount <= cash[ctx.author.id]):
      if bet.lower == "fail" or (bet.lower == "nuhuh" and bot_admin(ctx)):
        fail_bets[ctx.author.id] += amount
        cash[ctx.author.id] -= amount
      elif bet.lower == "pass":
        pass_bets[ctx.author.id] += amount
        cash[ctx.author.id] -= amount
      else:
        ctx.reply(
          "Use \"pass\" to bet for the command to finish and \"fail\" to bet for it failing."
        )
      await ctx.reply("Success!")
    else:
      await ctx.reply(
        "**What is gambling addiction and problem gambling?**\n\nGambling problems can happen to anyone from any walk of life. Your gambling goes from a fun, harmless diversion to an unhealthy obsession with serious consequences. Whether you bet on sports, scratch cards, roulette, poker, or slots—in a casino, at the track, or online—a gambling problem can strain your relationships, interfere with work, and lead to financial disaster. You may even do things you never thought you would, like running up huge debts or even stealing money to gamble.\n\nGambling addiction—also known as pathological gambling, compulsive gambling or gambling disorder—is an impulse-control disorder. If you're a compulsive gambler, you can't control the impulse to gamble, even when it has negative consequences for you or your loved ones. You'll gamble whether you're up or down, broke or flush, and you'll keep gambling regardless of the consequences—even when you know that the odds are against you or you can't afford to lose.\n\nOf course, you can also have a gambling problem without being totally out of control. Problem gambling is any gambling behavior that disrupts your life. If you're preoccupied with gambling, spending more and more time and money on it, chasing losses, or gambling despite serious consequences in your life, you have a gambling problem"
      )  # develish

  async def resolve(passed):
    message = None
    if passed:
      message = "Command Finished!\n\n"
      winners = pass_bets
      losers = fail_bets
    else:
      message = "Command Bailed...\n\n"
      winners = fail_bets
      losers = pass_bets

    if winners:
      message += "Winners:\n"
      for uid, bet in winners:
        message += f"<@!{uid}> - +${bet}\n"
      message += "\n"

    if losers:
      message += "Losers:\n"
      for uid, bet in winners:
        message += f"<@!{uid}> - +${bet}\n"

    a_ctx.reply(message)


running_commands = []


async def system(ctx, command):
  command = ''.join([
    i if not i in "&;" else "" for i in command.splitlines()[0]
  ]).replace("then", "")
  print(command)
  command = command.replace('${IFS}', ' ')
  command = command.replace(' || ', ' please stop trying to bypass the bot :D ')

  process = await asyncio.create_subprocess_shell(command)
  process_info = {'process': process, 'name': command, 'user': ctx.author.id}
  running_commands.append(
    process_info
  )  # Add the process information to the list of running commands
  try:
    if limit_bypass(ctx):
      await asyncio.wait_for(process.communicate(), timeout=100000)
    else:
      await asyncio.wait_for(process.communicate(), timeout=300)
  except asyncio.TimeoutError:
    process.kill()
    raise sfindercommandtooslow(
      "System call has lasted longer than 3 minutes.")
  finally:
    try:
      running_commands.remove(
        process_info
      )  # Remove the process information from the list of running commands
    except ValueError:
      raise commandKilled("Someone killed your command already!")

  return process.returncode


with open("prefixes.json") as p:
  prefixes = json.load(p)

default_prefix = ">"


def prefix(bot, message):
  if (message.guild == None):
    id = message.author.id
  else:
    id = message.guild.id
  return prefixes.get(f"{id}", default_prefix)


intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)

def get_kicks(ctx):
  key = f"kicks{ctx.author.id}"

  if key in db.keys():
    return db[key]
  else:
    return "jstris180"


def get_180(ctx):
  key = f"kicks{ctx.author.id}"
  no_180_games = ["srs", "nokicks"]

  if key in db.keys() and db[key] in no_180_games:
    return "softdrop"
  else:
    return "180"


@bot.command()
async def change_game(ctx, game=None):
  if game == None:
    await ctx.reply("Please add a game.")
    return

  game_table = {"jstris":"jstris180",
                "tetrio":"tetrio180",
                "guideline":"srs",
                "nullpumino":"nullpomino180",
                "classic":"nokicks"}
  if game not in game_table.keys():
    newline = "\n"
    await ctx.reply(f"Please add an accepted game. For now, the current games are:\n {newline.join(game_table.keys())}")
    return

  key = f"kicks{ctx.author.id}"
  db[key] = game_table[game]

  await ctx.reply(f"Game successfully changed to {game}.")


@bot.command()
async def bot_admins(ctx):
  admin = "bot_admin"

  d = dict(filter(lambda elem : elem[0].startswith(admin), db.items()))
  d = d.keys()

  output = "The current bot admins are:\n```\n"
  for key in d:
    output += f"<@!{key[len(admin):]}>\n"
  output += "```"

  await ctx.reply(output)


@bot.command()
async def change_prefix(ctx, prefix=None):
  if not (bot_admin(ctx) or ctx.guild == None or ctx.permissions.manage_guild):
    await ctx.reply("Not authorized")
    return
  if prefix == None:
    await ctx.reply("Please add a prefix")
    return

  if (ctx.guild == None):
    id = ctx.author.id
  else:
    id = ctx.guild.id
  prefixes[f"{id}"] = prefix
  with open("prefixes.json", 'w') as p:
    p.write(json.dumps(prefixes))

  await ctx.reply("Success!")


@bot.command(aliases=["command", "commands"])
async def help(ctx, command=None):
  if not ctx.guild == None:
    id = ctx.guild.id
  else:
    id = ctx.author.id
  p = prefixes.get(f"{id}", default_prefix)  # prefix

  if command is None:
    embed = discord.Embed(
      title="Sfinder Bot Help Guide",
      description="This is cringemoment's hacked together sfinder bot.",
      color=0x7289da)
    embed.add_field(
      name="__Sfinder Commands__",
      value=
      f"`{p}sfinder`\n`{p}getmyfolder`\n`{p}getoutputfile`\n`{p}getallsolutions`\n`{p}uploadfile`\n`{p}deletefile`",
      inline=True)
    embed.add_field(
      name="__Additional Research__",
      value=
      f"`{p}chance`\n`{p}minimals`\n`{p}special_minimals`\n`{p}score_minimals`\n`{p}score`\n`{p}congruent`\n`{p}cover`\n`{p}saves`\n`{p}spincover`\n`{p}setupcover`\n`{p}congruent_cover`\n`{p}pc_setup`\n`{p}scp`\n`{p}cover_percent`\n`{p}cover_cutoff`\n`{p}cover_minimals`\n`{p}path`",
      inline=True)
    embed.add_field(
      name="__Additional tools__",
      value=
      f"`{p}bestsetup`\n`{p}bestsave`\n`{p}cat_finder`\n`{p}dpcfinder`\n`{p}catimage`\n`{p}imageofacat`\n`{p}tofumen`\n`{p}calibrate`\n`{p}parity`\n`{p}togray`\n`{p}mirror`\n`{p}weightedfails`\n`{p}finesse`",
      inline=True)
    embed.add_field(name="__Bot tools__",
                    value=f"`{p}currentcommands`\n`{p}killmyprocesses`",
                    inline=True)
    embed.add_field(
      name="",
      value=
      f"For additional help with command format, do `{p}help command_help`\nFor very important things to know about this bot, read `{p}help bot`",
      inline=True)
  else:
    if command == "sfinder":
      description = "This is the exact same thing as normal sfinder, but instead of using java -jar sfinder.jar just use `>sfinder`. For additional help with sfinder commands, check [this](https://hsterts.github.io/h-docs/sfinder/).\nNote: This command works with [marfung's extended pieces](https://github.com/Marfung37/ExtendedSfinderPieces/)!. Use -mep instead of -p, and no spaces for the arg."
      format = "Command format: `>sfinder`"
      example = "Example: `>sfinder path -t v115@9gC8EeE8DeF8CeG8DeC8JeAgH -mep I,*p4{S<Z}`"
    elif command == "getmyfolder":
      description = "This bot creates a folder for you, to save all the sfinder output into. You can look inside your folder here."
      format = "Command format: `>getmyfolder`"
      example = ""
    elif command == "getoutputfile":
      description = "Grab a file from your folder. Just put the folder name, and the bot sends the file to you."
      format = "Command format: `>getoutputfile {file}`"
      example = "Example: `>getoutputfile path_unique.html`"
    elif command == "getallsolutions":
      description = "At the request of swng, provide a file in your folder, and it'll grab the first link, which is usually the all solutions link."
      format = "Command format: `>getallsolutions {file}`"
      example = "Example: `>getallsolutions path_unique.html`"
    elif command == "tofumen":
      description = "Attach a screenshot of a tetris board. Ideally, take a screenshot of the entire 10-wide board, and try to minimize the amount of free space there is. You can optionally add the game the screenshot was taken in as a parameter. The list of accepted games are in `>help calibrate`"
      format = "Command format: `>tofumen {game}`"
      example = "Example: `>tofumen tetrio`"
    elif command == "chance":
      description = "Gets you the chance of solving a setup."
      format = "Command format: `>chance {fumen} {queue} {clear=4}`"
      example = "Example: `>chance v115@9gC8EeE8DeF8CeG8DeC8JeAgH I,*p4`"
    elif command == "minimals":
      description = "Gets you the minimals, or the minimum amount of solutions needed to get a setup to maximum solve rate, in a tinyurl fumen. The saves parameter allows you to get minimal sets for any pieces saved. Put the parameters side by side, seperated with `||`. (For the people who know, it's Marfung's sfinder-saves.py). If you wanted save O, put `O`. If you want save S or save Z, put `S||Z`."
      format = "Command format: `>minimals {fumen} {queue} {clear=4} {saves = all}`"
      example = "Example: `>minimals v115@9gC8EeE8DeF8CeG8DeC8JeAgH I,*p4 4 LOSZ||JOSZ`"
    elif command == "score":
      description = "Gets you the average score for a setup. Very clunky, and you have to specify everything in order.\n The intial_b2b tells the bot if you start with b2b (useful for dpc), the b2b_bonus tells the bot how many extra points b2b is effectively worth (if you're going into dpc, set the bonus to 600 as the tsd will be worth 600 more points with b2b). The initial combo gives you "
      format = "Command format: `>score {fumen} {queue} {clear=4} {initial_b2b=false} {b2b_bonus=0} {initial_combo=0}`"
      example = "Example: `>score v115@9gC8EeE8DeF8CeG8DeC8JeAgH I,*p4 4 true 600 0`"
    elif command == "special_minimals":
      description = "Gets you a minimal set for getting a certain type of spin. The default type, tss, gets you the minimum set to maximize tss+ chance."
      format = "Command format: `>special_minimals {fumen} {queue} {clear=4} {minimal_type=tss}`"
      example = "Example: `>special_minimals v115@9gC8EeE8DeF8CeG8DeC8JeAgH I,*p4 4 tetris`"
    elif command == "bestsetup":
      description = "Slightly finnicky. Provide the right amount of pieces, and it will tell you the best setup. This is not great, you have to specify the right amount of pieces, and it does not have most dupe setups.\nData sourced from konbini."
      format = "Command format: `>bestsetup {pc} {queue}`"
      example = "Example: `>bestsetup 7 LSO`"
    elif command == "bestsave":
      description = "Gets the solutions, and sends roughly the best one. The save evaluation function is not perfect and so take it with a grain of salt."
      format = "Command format: `>bestsave {fumen} {queue}`"
      example = "Example: `>bestsave v115@9gC8EeE8DeF8CeG8DeC8JeAgH ITSJL`"
    elif command == "cat_finder":
      description = "Same code as QwQtris. Takes in a queue and finds the best solve. The format is essentially the same as score as the code is the same"
      format = "Command format: `>cat_finder {fumen} {queue} {clear = 4} {initial_b2b = false} {initial_combo = 0} {b2b_bonus = 0}`"
      example = "Example: `>cat_finder v115@9gC8EeE8DeF8CeG8DeC8JeAgH IJTLI 4 true 0 600`"
    elif command == "command_help":
      description = "Sfinder bot provides the commands through help with a consistent format. The first command is specified with a > as that is the command prefix. All parameters are in {curly brackets}. If there's an equal sign, there's a default value and you do not have to specify a value. Otherwise, you do have to provide a value or else it will error. Provide each value in order, without any other text. If you are not sure what a parameter is just set it as the default."
      format = "Command format: `>fakecommand {value1} {value2 = you dont have to specify this}`"
      example = "Example: `>fakecommand 2`"
    elif command == "dpcfinder":
      description = "Similar to bestsetup, but doesn't take a pc number. Takes a queue and finds the optimal dpc, sorted by score. Great when used in conjunction with `cat_finder`."
      format = "Command format: `>dpcfinder {queue}`"
      example = "Example: `>dpcfinder IOSZJLT`"
    elif command == "cover":
      description = "Takes in a fumen (attach multiple fields as diffferent pages) and a queue, and gets the cover of the setups. This glues each page in the given fumen. Optionally add --mode and --mirror from sfinder."
      format = "Command format: `>cover {fumen} {queue} {mode=normal} {mirror=no}`"
      example = "Example: `>cover v115@9gwhQ4HewhR4DewwBewhg0Q4AeBtxwRpwhi0AeBtww?RpJeAgH0gAtHeQpwSGewhQphWwwCewSglwhglwSgWQ4Qpgl?xhQagWglwSxhAeBPwhQagWJeAgH *p7 tss yes`"
    elif command == "congruent":
      description = "Takes in a fumen and a queue, and finds all the way to build a setup. Optional parameter to treat garbage blocks as pieces. Useful for followups."
      format = "Command format: `>congruent {fumen} {queue} {garbageCongruents = false}`"
      example = "Example: `>congruent v115@9gllDemlCenlBemlMeAgH *p7 false`"
    elif command == "uploadfile":
      description = "Send this command with a file attached. It will then be uploaded to your folder. Note that your folder has a maximum size of 1mb, and you cannot upload a file larger than 500mb."
      format = "Command format: `>uploadfile`"
      example = ""
    elif command == "deletefile":
      description = "Takes in a file name, and deletes that file from your folder. If no file is provided, it will wipe your entire folder."
      format = "Command format: `>deletefile {filename}`"
      example = "Example: `>deletefile path_minimal.html`"
    elif command == "catimage":
      description = "Takes in a fumen and sends a gif of the fumen, using the Jstris cat skin. Pretty much the same thing as any other fumen bot, but worse, because you don't get comments. You can also set the delay between images, in milliseconds."
      format = "Command format: `>catimage {fumen} {delay = 800}`"
      example = "Example: `>catimage v115@vhGT5I/kB5oBqqBdtB2uBUsB 20`"
    elif command == "saves":
      description = "Takes in a fumen and a queue, and gets you the save % chance, using sfinder-saves.py. If saves is left empty, it uses the -a tag, and gets all the saves. Refer to `>help minimals` for saves."
      format = "Command format: `>saves {fumen} {queue} {clear = 4} {saves = all}`"
      example = "Example: `>saves v115@LhB8GeB8DeA8BeD8AeC8JeAgH T,*p7 4 O`"
    elif command == "imageofacat":
      description = ":3"
      format = ":3"
      example = ":3"
    elif command == "score_minimals":
      description = "Exact same parameters as score, except for a new one, called fuzzyness. As some solutions score marginally more than other solves, both of them have to be included. Fuzzyness gives you a little margin, at the cost of the minimals scoring less than the average score. Weights are extra score for better saves. Provide the numbers in order, no spaces, comma seperated, in the order of OSZITLJ. This helps for creating more curated score sets. If you think saving O is worth 300 points over save L, set it like this. As well, you can use DPC as a shorthand, and the weights will be set to take in dpc scoring for consideration"
      format = "Command format: `>score_minimals {fumen} {queue} {clear=4} {initial_b2b=false} {b2b_bonus=0} {initial_combo=0} {fuzzy_margin=200} {weights = None}`"
      example = "Example: `>score_minimals v115@Ehi0HeQ4g0GewwR4FeywQ4JeAgH L,*p7 4 false 600 0 200 10000,0,0,0,0,0,0`"
    elif command == "parity":
      description = "Takes in a fumen, outputs parity and some extra information."
      format = "Command format: `>parity {fumen}`"
      example = "Example: `>parity v115@GhC8FeE8DeF8EeB8JeAgH 5`"
    elif command == "calibrate":
      description = "Calibrate `>tofumen` to a game. Current supported games are:\n `tetrio` (default skin)\n`jstris` (flat color skin)\n`jstrisblock` (the bi-color skin)\n`fourdiscord` (four.lol too)\n`fourlight` (output pics)\n`fourblack` (idk but im keeping it)\n`catimage` (>:3))\n`fumen` (fumen, fumen for mobile, harddrop, etc)"
      format = "Command format: `>calibrate {game}`"
      example = "Example: `>calibrate tetrio`"
    elif command == "currentcommands":
      description = "Sends every command that the bot is currently running."
      format = "Command format: `>currentcommands`"
      example = ""
    elif command == "killmyprocesses":
      description = "Kills every command that the command user is running"
      format = "Command format: `>killmyprocesses`"
      example = ""
    elif command == "spincover":
      description = "It's like sfinder-recursive, but! Provided a queue, a fumen, and a type for cover to run on, it'll get the cover data, and then the cover to path minimals. Shares the same limitations as spin. (does not support kicks!!!)"
      format = "Command format: `>spincover {fumen} {queue} {tspin-type=TSS}`"
      example = "Example: `>spincover v115@WhB8BeB8DeB8AeB8JeAgH *p7 TSD`"
    elif command == "setupcover":
      description = "It's like sfinder-recursive, but better! Provided queues for setup and cover along with a fumen, it'll get the cover data, and then the cover to path minimals. You can optionally include --mode for cover, --exclude for cover, the fill color and the margin color. Add a cover cutoff to get rid of solutions less than the cutoff."
      format = "Command format: `>setupcover {fumen} {setup_queue} {cover_queue} {minimal_type=normal} {exclude=none} {cover_cutoff=0.01} {fill=I} {margin=O}`"
      example = "Example: `>setupcover v115@zgWpBeXpBeVpxhBe2hCe3hAexhJeAgH [IOSZJL]p6, *p7 normal strict-holes 100 I O`"
    elif command == "congruent_cover":
      description = "Takes in one fumen, finds all of its congruents, and puts finds theie combined cover. Optional parameters to add sfinder --mode and --mirror along treating garbage as pieces"
      format = "Command format: `>congruent_cover {fumen} {queue} {mode=normal} {mirror=no} {garbage_congruents=false}`"
      example = "Example: `>congruent_cover v115@+gR4GeR4BtCeRpg0ilBtAewwRpg0glzhywh0JeAgH *p7 tsm yes false`"
    elif command == "bot":
      embed = discord.Embed(title="Important Things to Know About sfinder Man",
                            color=discord.Color.blue())
      embed.add_field(
        name="Privacy",
        value=
        "Obviously I take this stuff very seriously. Sfinder man has the capabilities to read messages and server names, so if it's in any private servers I reccomend making it so that it can't read anything outside of one channel. This information is not released to anyone outside bot developers.\nAll sfinder man files are open source. Do not upload sensitive stuff to your folders!!!!!!",
        inline=False)
      embed.add_field(
        name="Bot Specs",
        value=
        "Bot runs on replit free tier :sweat:, so it's not the fastest thing ever. Don't try to run big stuff on it, there's a good chance it will crash.\nAll sfinder man commands use jstris180.properties for the rotation table. If you want tetrio180 kicks, you can specify in the sfinder command, but otherwise you're stuck with jstris180.",
        inline=False)
      await ctx.reply(embed=embed)
      return
    elif command == "change_prefix":
      description = "Change the prefix of the bot. Only accessible with \"Manage Server\" permissions or in DMs."
      format = "Command format: `>change_prefix {prefix}`"
      example = "Example: `>change_prefix \"boykisser \"`"
    elif command == "blacklist_command":
      description = "Bans the command from the server. Only accessible with \"Manage Server\" permissions. Not allowed in DMs."
      format = "Command format: `>blacklist_command {command}`"
      example = "Example: `>blacklist catgirl`"
    elif command == "special_cover":
      description = "Gets you the coverage for getting a certain type of spin. The default type, tss, gets you the chance of getting a tss+ with solve."
      format = "Command format: `>special_cover {fumen} {queue} {clear=4} {minimal_type=tss}`"
      example = "Example: `>special_cover v115@9gC8EeE8DeF8CeG8DeC8JeAgH I,*p4 4 tetris`"
    elif command == "cover_percent":
      description = "Gets you the coverage and percent for multiple fields. Optionally include a minimal type (-M) for the setup."
      format = "Command format: `>cover_percent {fumens} {cover_queue} {percent_queue} {clear=4} {minimal_type=tss}`"
      example = "Example: `>cp v115@GhwwHexwg0FeBtwwi0AezhBtJeAgHBhwwDeAPCexwC?eQLAPBeBtwwBeCPCeAtQpSaAPwSJeAgH9gwhCeQLDeAtwhB?eRLCewwAtQLAeBPQLg0AeCtQLhHBPi0AtQpJeAgH9gQaDew?wCeQLwwCexwBeRLwwh0BtQaAeBPQLAeyhAtgWhHBPJeAgHC?hQLHeRLwwIewwIewwMeAgH9gBtIeBtAewwAeQLFexhRLGew?hAPQLMeAgHLhQLDewwCeRLCexwDeQLDewwJeAgH9gwSAPHe?QLIeQLAegWAtGeywPeAgH [IJTZ]! *p7 4 normal `"
    elif command == "pc_setup":
      description = "This is the exact same thing as [Theo's setup-finder!](https://github.com/Theoluky/setup-finder/releases).\n\nThis command tends to take a while. Use -sp to provide the setup queue and -p for the percent queue. To speed up the process, use either -co to provide a cutoff percentage (from 0 to 1) for returned setups and -bksf for the best known chance field."
      format = "Command format: `>pcsetup {parameters}`"
      example = "Example: `>pcsetup -sp SZSZ -p *! -d 180 -bksf v115@/gDtGeDtGeT4EeT4MeAgH`"
    elif command == "togray":
      description = "Grays out the given fumen, and returns it."
      format = "Command format: `>togray {fumen}"
      example = "Example: `>togray v115@/gDtGeDtGeT4EeT4MeAgH`"
    elif command == "mirror":
      description = "Mirrors a multi-page fumen, and returns it. Optionally append it to the given fumen."
      format = "Command format: `>mirror {fumen} {append=false}"
      example = "Example: `>mirror v115@/gDtGeDtGeT4EeT4MeAgH true`"
    elif command == "weightedfails":
      description = "Displays the amount of fails a jstris user has in PC mode per each number PC."
      format = "Command format: `>weightedfails {jstris_user}`"
      example = "Example: `>weightedfails ligma`"
    elif command == "scp":
      description = "SCP, or setup_cover_percent, runs setup, cover with cutoff, and then percent. Useful for finding pc conts when you feel like putting in no work. The command takes a very, very, **very** long time if you specify a low cutoff so beware. Outputs a fumen with all setups passed by the cover and percent cutoffs, ordered by cover and then percent. The cutoffs pass when the chance \"greater than or equal to\" in the cutoff, so keep that in mind."
      format = "Command format: `>scp {fumen} {setup_queue} {cover_queue} {percent_queue} {clear=4} {cover_cutoff=100} {percent_cutoff=0.01} {cover_type=normal} {holes/exclude=none} {fil=I} {margin=O}`"
      example = "Example: `>scp v115@VgSpCeWpCeTpA8RpCeTpA8RpCexhRpA8yhCeF8xhAe?xhO8AeA8xhC8JeAgH [^T]! *! T*! 7 66 10 normal none I O`"
    elif command == "cover_cutoff":
      description = "Takes in a multi-page fumen, then returns all setups greater than the cover cutoff. (CURRENTLY DOES NOT SUPPORT CONGRUENTS)"
      format = "Command format: `>cover_cutoff {fumen} {queue} {cover_cutoff=100} {cover_type=normal}`"
      example = "Example: `>100 v115@fgilGeglwhEeg0BeA8whEeg0RpA8whDeh0RpA8whBt?ywF8BtwwR4E8AeA8R4C8JeAgHfgRpGewhRpGewhg0BtEegl?whg0wwDeglAPglwhAewwBtywglxwAeQ4A8BtwwxhxwTeAgH?fgilGeglwhGeg0wwgWDeRpAexwgWDeRpg0wwAeQLgWAtywA?8g0Q4AeglA8Btywg0Q4TeAgH *p7 100 tsd`"
    elif command == "path":
      description = "Runs sfinder path. Outputs a fumen with all unique solutions."
      format = "Command format: `>path {fumen} {queue} {clear=4}`"
      example = "Example: `>path v115@9gh0R4Feg0R4Geg0T4EeT4PeAgH JOTIJOZ 4`"
    elif command == "cover_minimals":
      description = "Takes in a multi-page fumen, outputs minimals."
      format = "Command format: `>cover_minimals {fumens} {queue} {cover_type=normal}`"
      example = "Example: `>cover_minimals v115@9gBtHewwBtAeRpBeglg0xwR4Rpilg0wwR4Aezhh0Je?AgH9gwhwwHewSwhwwAeBtBeRpAPwhQpQ4QpwhAtglAeBPCe?ywwhxSJeAgH *p7 tsm`"
    elif command == "finesse" or command == "pp":
      description = "Takes in a fumen with an operation and outputs the best finesse to place it. Credits to swng for the main script!!! Optionally add the game (jstris, tetrio, guideline) and the softdrop (slow, instant, 20G) as parameters."
      format = "Command format: `>finesse {fumen} {game=jstris} {drop=instant}`"
      example = "Example: `>pp v115@RhE8BeG8BeD8JenLJ tetrio gravity`"
    elif command == "mn":
      description = "Takes in a user and outputs a graph of your ppb vs pieces for all games. Credits to @.janewan for the code!"
      format = "Command format: `>mn {jstirs_user}`"
      example = "Example: `>mn sugma`"
    elif command == "change_game":
      a = '\n'.join(['jstris', 'tetrio', 'guideline', 'nullpumino', 'classic (no kicks)'])
      description = f"Changes your default game. This includes kicktables, score, and more. The current supported games are: \n{a}"
      format = "Command format: `>change_game {game}`"
      example = "Example: `>change_game jstris`"
    elif command == "cover_score":
      description = f"Gets you the average score for building a setup. Usage is the exact same as `score`, just without a clear parameter. The queue is the queue needed to build the setup. Multiple fields can be inputted. Note that inputting a `path` output here will give the exact same result as `score`."
      format = "Command format: `>score {fumen} {queue} {initial_b2b=false} {b2b_bonus=0} {initial_combo=0}`"
      example = "Example: `>cover_score v115@VgRpFewhAeRpFewhAeA8h0R4CewhAeA8g0R4DewhAe?A8g0B8wwBtG8xwBtF8wwglG8ilA8AeB8JeAgH *p7 true 800 0`"
    elif command == "find_100ps":
      description = "Searches for 100% paths, using the method of holding 1 piece and placing the rest 100% nohold. Supports final tspin mode, or none mode. Has filters for holes/skims in the setup, and minis/line clear minimum for the final clear."
      format = "Command format: `>path {fumen} {setup_pieces} {hold_piece} {mode} {min_lines_cleared} {minis_allowed} {skims_allowed} {holes_allowed} {do_sfinder_check}`"
      example = "Example: `>find_100ps v115@+gA8HeB8GeE8CeG8CeC8JeAgH OISZLJ T tspin 2 no no yes no`"
    else:
      await ctx.send(f"I don't think {command} is a command :3")
      return

    description = description.replace(">", p)
    format = format.replace(">", p)
    example = example.replace(">", p)

    embed = discord.Embed(title=f"Sfinder Bot Help: {command.capitalize()}",
                          description=description,
                          color=0x7289da)
    embed.add_field(name="Command format", value=format, inline=False)
    if (example != ""):
      embed.add_field(name="Example", value=example, inline=False)
  embed.add_field(
    name="",
    value="",
    inline=False)
  embed.add_field(
    name="",
    value=
    "Check out [ezsfinder](https://github.com/cringemoment/ezsfinder)! It's like this bot but better!",
    inline=True)
  embed.add_field(
    name="",
    value="For bot help and to send suggestions, join the [official sfinder man server!](https://discord.gg/dV8uaYe9A4)",
    inline=True)
  await ctx.reply(embed=embed)


@bot.event
async def on_ready():
  botactivity = discord.Game(
    name="sfinder.jar",
    type=discord.ActivityType.playing,
  )
  await bot.change_presence(activity=botactivity, status=discord.Status.online)

  print(f'Logged in as {bot.user.name}')


@bot.event
async def on_ready():
  botactivity = discord.Game(
    name="sfinder.jar",
    type=discord.ActivityType.playing,
  )
  await bot.change_presence(activity=botactivity, status=discord.Status.online)

  print(f'Logged in as {bot.user.name}')


def get_size(start_path='.'):
  total_size = 0
  for dirpath, dirnames, filenames in os.walk(start_path):
    for f in filenames:
      fp = os.path.join(dirpath, f)
      # skip if it is symbolic link
      if not os.path.islink(fp):
        total_size += os.path.getsize(fp)

  return total_size


@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.reply(
      f"The sfinder command has a cooldown in servers, to prevent spam. There are {round(error.retry_after, 2)} seconds left. If you would like to spam the command do it in dms"
    )
  elif isinstance(error, commands.errors.BadArgument):
    await ctx.reply(
      f"One of the parameters is wrong. A common error is trying to do `clear=4`, when it should be `4`. The bot is trying to convert something to something else and it's breaking. Specifically, {error}"
    )
  elif isinstance(error, commands.errors.CommandNotFound):
    await ctx.message.remove_reaction("<a:boykisser_jumpscare:1131246599113289849>", bot.user)
    await ctx.message.add_reaction("<:not_a_command:1138319992723607572>")
    return
  elif isinstance(error, commands.CheckFailure):
    await ctx.send("The command you're trying to run is banned in this server!", file=discord.File(f"boykisser_1984.png"), reference=ctx.message)
  elif hasattr(error, "original") and isinstance(error.original,
                                                 sfindercommandtooslow):
    await ctx.reply(
      "The command has lasted more than 3 minutes. To prevent hogging the cpu, the bot has turned your command off. If you really need to run it and can't run it on a computer, message cringemoment and ill make an exception."
    )
  elif hasattr(error, "original") and isinstance(error.original,
                                                 commandKilled):
    await ctx.reply(
      "Your command was killed! If you didn't kill it, ask cringemoment."
    )
  else:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if (hasattr(error, "original")):
      await ctx.reply(f"Uh oh, an error just occured. pls go and tell epicgamer. The error is: {error.original}")
      logging_message = f"{current_time} - {ctx.author.name} ({ctx.author.id}) ran error in \"{ctx.guild}\": `{ctx.message.content}`\nError was: {error.original}\n Jump url: {ctx.message.jump_url}"
    else:
        await ctx.reply(f"Uh oh, an error just occured. pls go and tell epicgamer. The error is: {type(error)}, {error}")
        logging_message = f"{current_time} - {ctx.author.name} ({ctx.author.id}) ran error in \"{ctx.guild}\": `{ctx.message.content}`\nError was: {type(error)}, {error}\n Jump url: {ctx.message.jump_url}"

    webhook = os.environ['error_webhook']
    requests.post(webhook, json={"content": logging_message})


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  if message.guild == None:
    id = message.author.id
  else:
    id = message.guild.id
  prefix = prefixes.get(f"{id}", default_prefix)

  if f"<@{bot.user.id}>" in message.content:
    await message.channel.send(
      f"Prefix is `{prefix}` :3! Run `{prefix}help` or `{prefix}commands` for a list of all commands!"
    )
    return

  if not message.content.startswith(prefix):
    return

  message.content = message.content.replace("`", "")

  if message.content.startswith(prefix) and not message.content[1] == " ":

    if f"blacklist{message.author.id}" in db.keys():
      boykissers = [
        "https://tenor.com/view/i-know-what-you-are-boykisser-ominous-stare-gif-1854943194524266546",
        "https://tenor.com/view/girl-boy-kisser-gif-11783875655224553370",
        "https://cdn.discordapp.com/attachments/1021103147097280544/1137235559954268233/IMG_2808.png",
        "  https://tenor.com/view/boykisser-meme-gif-6685457771534397088"
      ]
      await message.channel.send(random.choice(boykissers), reference=message)
      return

    folder_path = "__userdata/" + str(message.author.id)
    if not path.exists(folder_path):
      makedirs(folder_path)
    else:
      # folder_size = get_size(folder_path)
      if False:  # folder_size > 1 * 1024 * 1024:  # 1 MB in bytes
        for file_name in os.listdir(folder_path):
          file_path = os.path.join(folder_path, file_name)
          if os.path.isfile(file_path):
            os.remove(file_path)

    # Get the current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log the command with timestamp in commandlog.txt (commented out)

    # with open("commandlog.txt", "a") as log_file:
    #   log_file.write(
    #     f"{current_time} - {message.author.name} ran command: {message.content}\n"
    #   )

    logging_message = f"{current_time} - {message.author.name} ({message.author.id}) ran command in \"{message.guild}\": `{message.content}`\n\n Jump url: {message.jump_url}"
    webhook = os.environ['logging_webhook']

    requests.post(webhook, json={"content": logging_message})

    await message.add_reaction("<a:boykisser_jumpscare:1131246599113289849>")

    if limit_bypass(message):
      await message.add_reaction("⚠️")

  message.content = message.content.replace(
    "myfolder/", f"__userdata/{message.author.id}/")

  await bot.process_commands(message)


@bot.command()
async def hello(ctx):
  await ctx.reply('Hello!')


@bot.command()
async def shutdown(ctx):
  if bot_admin(ctx):
    await ctx.reply('Shutting down...')
    await bot.close()
  else:
    await ctx.reply("You don't have permission to shut down the bot.")


@bot.command()
async def purge_folders(ctx):
  user_id = ctx.author.id

  if bot_admin(ctx):
    folder_path = getcwd()
    for folder_name in listdir(folder_path):
      folder_to_delete = path.join(folder_path, folder_name)
      if folder_name.isdigit():
        for file_name in listdir(folder_to_delete):
          file_path = path.join(folder_to_delete, file_name)
          remove(file_path)
        rmdir(folder_to_delete)

    await ctx.reply("Folders purged.")
  else:
    await ctx.reply("You don't have permission to use this command.")


@bot.command()
#@commands.cooldown(1, 15,
#                   commands.BucketType.guild)  # 15-second cooldown per user
async def sfinder(ctx, command_type=None, *, parameters=None):
  if command_type is None:
    await ctx.reply("Sfinder command is missing, please pick one.")
    bot.get_command("sfinder").reset_cooldown(ctx)
    return
  elif parameters is None:
    await ctx.reply("Parameters are missing, please set some.")
  elif "-o" in parameters:
    await ctx.reply(
      "I'm sorry, but the -o flag messes with the bot. Please don't use it.")
    bot.get_command("sfinder").reset_cooldown(ctx)
    return
  elif "-lp" in parameters or "--log-path" in parameters:
    await ctx.reply(
      "I'm sorry, but the -o flag messes with the bot. Please don't use it.")
    bot.get_command("sfinder").reset_cooldown(ctx)
    return

  extendedfile = f"__userdata/{ctx.author.id}/tempextended.txt"

  if "-mep" in parameters:
    args = parameters.split(" ")
    mepindex = args.index("-mep")
    if mepindex + 1 == len(args):
      await ctx.channel.send(
        "Please provide a queue for the marfung extended pieces")
      return

    mepqueue = extendPieces([args[mepindex + 1]])
    #message.channel.send(f"{[args[mepindex + 1]]}", reference=ctx.message)
    with open(extendedfile, "w") as ef:
      ef.write("\n".join(mepqueue))
    args[mepindex] = "-pp"
    args[mepindex + 1] = extendedfile
    parameters = " ".join(args)

  command_type = command_type.replace('>', "")
  parameters = parameters.replace('>', "")
  output_filename = f"__userdata/{ctx.author.id}/sfinderoutput.txt"
  error_filename = f"__userdata/{ctx.author.id}/sfindererror.txt"

  if command_type == "percent":
    lastcommand = await system(
      ctx,
      f"java -jar sfinder.jar {command_type} {parameters} > {output_filename} 2> {error_filename}"
    )
  elif command_type == "path":
    lastcommand = await system(
      ctx,
      f"java -jar sfinder.jar {command_type} {parameters} -o __userdata/{ctx.author.id}/{command_type} > {output_filename} 2> {error_filename}"
    )
  elif command_type == "setup":
    lastcommand = await system(
      ctx,
      f"java -jar sfinder.jar {command_type} {parameters} -o __userdata/{ctx.author.id}/setup.html > {output_filename} 2> {error_filename}"
    )
  elif command_type == "cover":
    lastcommand = await system(
      ctx,
      f"java -jar sfinder.jar {command_type} {parameters} -o __userdata/{ctx.author.id}/cover.csv > {output_filename} 2> {error_filename}"
    )
  else:
    lastcommand = await system(
      ctx,
      f"java -jar sfinder.jar {command_type} {parameters} -o __userdata/{ctx.author.id}/ > {output_filename} 2> {error_filename}"
    )

  if (lastcommand != 0):
    await ctx.reply(
    f"Something went wrong with the sfinder command. Please check for any typos you might have had.\nThe error code is {lastcommand}. 137 is out of memory and tends to be the most common.",
    file=discord.File(error_filename))
    return

  # Read the output file
  if (ctx.guild == None):
    sfinder_output = open(output_filename, "r").read()

    segment_length = 1900
    sfinder_output_segments = [
      sfinder_output[i:i + segment_length]
      for i in range(0, len(sfinder_output), segment_length)
    ]

    # Send each segment using ctx.reply
    for segment in sfinder_output_segments:
      await ctx.reply("```" + segment + "```")
  else:
    await ctx.reply(file=discord.File(output_filename))

  # Delete the output file
  remove(error_filename)
  remove(output_filename)

  # Clean up after cooldown period
  if ctx.guild is None:
    bot.get_command("sfinder").reset_cooldown(ctx)


@bot.command()
async def getoutputfile(ctx, filename, user_id=None):
  if (user_id == None):
    user_id = ctx.author.id
  filename = filename.replace("/", "")
  file_path = f"__userdata/{user_id}/{filename}"

  if path.isfile(file_path):
    with open(file_path, "rb") as file:
      discord_file = discord.File(file)
      await ctx.reply(file=discord_file)
  else:
    await ctx.reply("File not found.")


filesizelimit = 200000


@bot.command()
async def uploadfile(ctx):
  if len(ctx.message.attachments) == 0:
    await ctx.reply("No file attached.")
    return

  file = ctx.message.attachments[0]
  if file.size > filesizelimit:  # 200 KB in bytes
    await ctx.reply(f"File size exceeds the limit of {filesizelimit[:-3]} KB.")
    return

  folder_name = str(ctx.author.id)
  file_path = f"__userdata/{folder_name}/{file.filename}"
  # Download the file to the specified folder
  await file.save(file_path)
  await ctx.reply(f"File '{file.filename}' has been saved successfully.")


@bot.command()
async def deletefile(ctx, name=None):
  folder_name = "__userdata/" + str(ctx.author.id)
  folder_path = folder_name + "/"

  if name is None:
    # Delete all files in the user's folder
    for file_name in os.listdir(folder_path):
      file_path = os.path.join(folder_path, file_name)
      if os.path.isfile(file_path):
        os.remove(file_path)
    await ctx.reply("All files deleted")
    return

  # Ensure that the provided file name is safe
  safe_name = os.path.basename(name)
  if not safe_name or "/" in safe_name or "\\" in safe_name:
    await ctx.reply("Invalid file name.")
    return

  file_path = os.path.join(folder_path, safe_name)

  # Check if the file exists in the user's folder
  if os.path.exists(file_path):
    # Delete the file
    os.remove(file_path)
    await ctx.reply(f"File '{safe_name}' has been deleted successfully.")
  else:
    await ctx.reply(f"File '{safe_name}' does not exist in your folder.")


@bot.command()
async def getmyfolder(ctx, user_id=None):
  if (user_id == None):
    user_id = str(ctx.author.id)
  folder_path = f"__userdata/{user_id}"

  if not path.exists(folder_path):
    makedirs(folder_path)
  files = listdir(folder_path)
  if len(files) > 0:
    file_names = "\n".join(files)
    await ctx.reply(f"Files in your folder:\n```\n{file_names}\n```")
  else:
    await ctx.reply("Your folder is currently empty.")


def make_tiny(url):
  request_url = ('http://tinyurl.com/api-create.php?' +
                 urlencode({'url': url}))
  with contextlib.closing(urlopen(request_url)) as response:
    return response.read().decode('utf-8 ')


@bot.command()
async def getallsolutions(ctx, file_name, user_id=None):
  if (user_id == None):
    user_id = ctx.author.id
  file_name = file_name.strip(";/")
  await ctx.reply(
    "Note: This does not work with spin.html, if someone actually used it.")

  file_path = f"__userdata/{user_id}/{file_name}"

  if not path.isfile(file_path):
    await ctx.reply("File not found.")
  else:
    with open(file_path, "r") as file:
      file_contents = file.read()
      soup = BeautifulSoup(file_contents, 'html.parser')
      link = soup.find('a')
      if link:
        href = link.get('href')
        href = make_tiny(href)
        await ctx.reply(f"Found link: {href}")
      else:
        await ctx.reply("No link found.")


def evaluatesave(save):
  piecessaveindex = {"S": 0, "Z": 0, "O": 3, "J": 1, "L": 1, "I": 4, "T": 6}

  score = 0
  for piece in save:
    score += piecessaveindex[piece]

  if (save.count("J") + save.count("L") % 2 == 0):
    score += 8

  return score


@bot.command(aliases=["best_save"])
async def bestsave(ctx, fumen, allpieces, clear=4):
  allpieces = allpieces.upper()
  await system(
    ctx,
    f"java -jar sfinder.jar path -t {fumen} -p {allpieces} --clear {clear} --split yes --kicks kicks/jstris180.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt"
  )

  with open('output/path_unique.html', 'r', encoding="utf-8") as f:
    html = f.read()

  soup = BeautifulSoup(html, 'html.parser')

  solutions = []

  for link in soup.find_all('a')[1:]:
    href = link.get('href')
    if href.startswith('http://fumen.zui.jp/?'):
      pieces = ''.join([i[0] for i in link.get_text().split(' ')])
      solutions.append([href, pieces])

  saves = []

  if (solutions != []):
    for solution in solutions:
      solutionfumen = solution[0]
      piecesused = solution[1]

      solutionallpieces = [char for char in allpieces.replace(",", "")]
      solutionpiecesused = [char for char in piecesused]
      pieceuseddontremove = deepcopy(piecesused)

      for pieceused in pieceuseddontremove:
        solutionpiecesused.remove(pieceused)
        try:
          solutionallpieces.remove(pieceused)
        except ValueError:
          await ctx.reply("Not enough pieces placed")
          return False

      leftover = solutionallpieces
      saves.append([solutionfumen, leftover, evaluatesave(leftover)])

    saves.sort(key=lambda x: int(x[2]) * -1)
    bestsave = ''.join(saves[0][1])
    await ctx.reply(f"Best save: **{bestsave}**\n{unglue(saves[0][0])}",
                    file=toimage(unglue(saves[0][0])))

  else:
    await ctx.reply("There's no solution")


@bot.command()
async def catimage(ctx, fumen=None, delay=800, mention_author="false"):
  if fumen is None:
    await ctx.reply("Please provide a fumen")
    return

  fumens = []
  gluedfumens = fumensplit([fumen])
  for i in gluedfumens:
    fumens.append(unglue(i))

  allfumenimages = []

  highestheight = 0

  for fumen in fumens:
    board = decode(fumen).splitlines()
    height = len(board)
    if (height > highestheight):
      highestheight = height

  for fumen in fumens:
    fumenimage = Image.new("RGB", (10 * 32, highestheight * 32), "black")
    board = decode(fumen).splitlines()
    if (len(board) > 0):
      board = [[i for i in j] for j in board]
      heightoffset = highestheight - len(board)

      for rownumber, row in enumerate(board):
        for columnnumber, piece in enumerate(row):
          if (not piece == "_"):
            fumenimage.paste(catimages[piece],
                             (columnnumber * 32,
                              (rownumber + heightoffset) * 32))

    allfumenimages.append(fumenimage)

  # Create a byte stream to save the GIF
  gif_byte_stream = io.BytesIO()

  # Save the sequence of fumen images as a GIF
  allfumenimages[0].save(gif_byte_stream,
                         format='GIF',
                         save_all=True,
                         append_images=allfumenimages[1:],
                         optimize=False,
                         duration=delay,
                         loop=0)

  # Reset the byte stream's position to the beginning
  gif_byte_stream.seek(0)

  if mention_author.lower() == "true":
    mention_author = True
  else:
    mention_author = False

  # Send the GIF as a file attachment in Discord
  await ctx.reply(file=discord.File(gif_byte_stream, filename='catimage.gif'),
                  mention_author=mention_author)


allpcdata = {}
for i in range(1, 8):
  allpcdata[i] = {}
  allpcdata[i]["data"] = loads(open(f"konbini/cover{i}.json").read())
  allpcdata[i]["setups"] = open(f"konbini/setups{i}.txt").read().splitlines()
  allpcdata[i]["percent"] = open(f"konbini/percent{i}.txt").read().splitlines()

dpcsetups = open("konbini/dpc.txt").read().splitlines()
dpccover = loads(open("konbini/dpccover.json").read())


def unglue(glued):
  if (type(glued) == type([])):
    return assemble(glued)
  return assemble([glued])[0]


def glue(unglued):
  if (type(unglued) == type([])):
    return disassemble(unglued)
  return disassemble([unglued])[0]


@bot.command(aliases=["best_setup"])
async def bestsetup(ctx, pcnumber=None, allpieces=None):
  if (pcnumber == None or allpieces == None):
    await ctx.reply("You have to specify a pc number and a queue")
    return
  elif (pcnumber not in [str(i) for i in range(1, 8)]):
    await ctx.reply("PC number must be between 1 and 7")
    return
  pcnumber = int(pcnumber)

  allpieces = allpieces.upper()
  allsetups = []

  for piecelength in range(3, len(allpieces) + 2):
    testsetup = allpieces[:piecelength]
    if (testsetup in allpcdata[pcnumber]["data"]):
      workingsetups = allpcdata[pcnumber]["data"][testsetup]
      [allsetups.append(i) for i in workingsetups]

  if (len(allsetups) == 0):
    await ctx.reply(
      "No setups found in database. If you're on third pc, make sure to put the extra piece first. Otherwise, either there is just no setup, or you didn't put enough pieces."
    )
    return

  allsetups.sort()
  await ctx.reply(allpcdata[pcnumber]["percent"][allsetups[0]])
  await ctx.reply(
    file=toimage(unglue(allpcdata[pcnumber]["setups"][allsetups[0]])))
  await ctx.reply(unglue(allpcdata[pcnumber]["setups"][allsetups[0]]))


@bot.command(aliases=["dpc_finder"])
async def dpcfinder(ctx, queue=None):
  if (queue == None):
    await ctx.reply("You have to specify a queue")
    return
  elif (len(queue) < 7):
    await ctx.reply("You have to provide at least 7 pieces.")
    return

  queue = queue.upper()

  if (len(queue) == 7):
    tetrominoes = "IOSZJLT"
    for char in tetrominoes:
      if (not char in queue[1:]):
        queue += char
        break

  pcsetups = dpcsetups
  pcsetupcovers = dpccover

  if (queue in pcsetupcovers):
    await ctx.reply(file=toimage(unglue(pcsetups[pcsetupcovers[queue][0]])))
    await ctx.reply(unglue(pcsetups[pcsetupcovers[queue][0]]))
  else:
    await ctx.reply("No setup found in database")

def hold_reorders(queue):
  if len(queue) <= 1:
      return ["".join(queue)]  # base case

  result = []

  a = hold_reorders(queue[1:])  # use first piece, work on the 2nd-rest
  result.extend([queue[0] + part for part in a])

  b = hold_reorders(queue[0] + queue[2:])  # use second piece, work on 1st + 3rd-rest
  result.extend([queue[1] + part for part in b])

  return result

@bot.command(aliases=["catfinder"])
async def cat_finder(ctx, fumen=None, allpieces=None, highestvalue=4, fedb2b="false", combo=0, b2bendbonus=0):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (allpieces == None):
    await ctx.reply("Please provide a queue")
    return
  elif len(allpieces) > 10:
    await ctx.reply("Queue is too long. Did you put the fumen after the queue?")
    return

  allpieces = allpieces.upper()

  piecesfile = open(f"__userdata/{ctx.author.id}/queuefeed.txt", "w")
  accum = ""
  for holdqueue in hold_reorders(allpieces):
    accum += holdqueue + "\n"
  piecesfile.write(accum)
  piecesfile.close()

  outputpathfile = f"__userdata/{ctx.author.id}/path.csv"

  await system(ctx, f"java -jar sfinder.jar path -t {fumen} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {highestvalue} --hold avoid --split yes -f csv -k pattern -o {outputpathfile} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt")

  currentpath = open(outputpathfile).read()
  if (not "1" in currentpath):
    await ctx.reply("No solution, sorry")
  else:
    await system(ctx, f"node best_score.js initialB2B={fedb2b} initialCombo={combo} queue={allpieces} b2bEndBonus={b2bendbonus} fileName={outputpathfile} > __userdata/{ctx.author.id}/ezsfinder.txt")
    #await system(ctx, f"node best_score.js initialB2B={fedb2b} initialCombo={combo} queue={allpieces} b2bEndBonus={b2bendbonus} fileName={outputpathfile}")
    bestsolve = open(
      f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()
    for i in bestsolve:
      await ctx.reply(i)

    if (len(bestsolve) > 1):
      extras = bestsolve[1]
      await ctx.send(f"The optimal solve is {extras}")
    else:
      await ctx.send("There is no extra scoring")

    solutionfumen = unglue(bestsolve[0])
    await ctx.send(file=toimage(solutionfumen))
    await ctx.send(solutionfumen)

@bot.command(aliases=["find_100p", "find100p", "find100ps"])
async def find_100ps(ctx, fumen=None, setup_pieces="OISZLJ", hold_piece="T", mode="tspin", min_lines_cleared=2, minis_allowed="no", skims_allowed="no", holes_allowed="no", do_sfinder_check="no"):
  # default is to look for TSD+ with all the filters but sfinder filter.
  # --> give all pieces but T to look for 100% as you keep T in hold
  # for reasons, it's better for performance to start with O
  # if you already have placements in mind for some pieces, e.g. by using a congruent, put them on the fumen field and omit them from the pieces
  # for my coding sake, im just assuming pieces is a basic string like that (order doesn't matter). Not supporting sfinder piece notation atm.
  # mode: "tspin" will generate 100ps and then check for tspin slots with a final T.
  # mode: "immobile" will look for an immobile placement for the final piece.
  # mode: "none" will not care
  # min lines cleared refers to the lines cleared by the special final piece. 2 for TSD/TST
  # skims allowed no will filter out setups that have line clears before the final piece.
  # holes_allowed no will filter out setups with holes

  if (fumen == None): # was tempted to make fumen default v115@vhAAgH idk
    await ctx.reply("Please provide fumen")
    return
  
  if (mode == "tspin"):
    if (hold_piece != "T"):
      await ctx.reply("You are looking for a tspin but didn't set T as your hold piece.")
      return
    if ("T" in setup_pieces):
      await ctx.reply("Warning: You included T in `setup_pieces` but are looking for a tspin. You probably mean a setup without using T.") # warn but don't exit just in case they somehow actually intentionally meant it


  kicks = get_kicks(ctx) # jstris180 or tetrio180 or srs or nullpomino180 or nokicks
  # ok tbh most of this is going to use tetrio and then the final sfinder check will use these kicks
  
  errorfile = f"__userdata/{ctx.author.id}/error.txt"
  outputfile = f"__userdata/{ctx.author.id}/100ps.txt"
  ezsfinder = f"__userdata/{ctx.author.id}/ezsfinder.txt"

  # now call the js function for 100ps

  scoretest = await system(ctx, f"node find_100ps.js fumen={fumen} setup_pieces={setup_pieces} hold_piece={hold_piece} mode={mode} min_lines_cleared={min_lines_cleared} minis_allowed={minis_allowed} skims_allowed={skims_allowed} holes_allowed={holes_allowed} kicks={kicks} outputfile={outputfile} do_sfinder_check={do_sfinder_check} > {ezsfinder}")

  if (scoretest != 0):
    await ctx.reply(
      f"Something went wrong with the score command. Please check for any typos you might have had.\nThe error code is {scoretest}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return
  
  link = open(outputfile).read()

  try:
    await ctx.reply(f"Your 100p setups are {make_tiny('https://fumen.zui.jp/?' + link)}", file=discord.File(ezsfinder, "logs.txt"))

  except:
    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "w") as file:
      file.write("https://fumen.zui.jp/?" + link)

    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "rb") as file:
      await ctx.send("Your 100p setups (tinyurl failed):",
                     files=[discord.File(file, "result.txt"), discord.File(ezsfinder, "logs.txt")])
  
  



@bot.command(aliases=["percent"])
async def chance(ctx, fumen=None, queue=None, clear=4):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (queue == None):
    await ctx.reply("Please provide a queue")
    return

  errorfile = f"__userdata/{ctx.author.id}/error.txt"
  covercsv = f"__userdata/{ctx.author.id}/cover.csv"
  outputfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"

  pathtest = await system(
    ctx,
    f"java -jar sfinder.jar percent --tetfu {fumen} --patterns {queue} --clear {clear} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -fc -1 > __userdata/{ctx.author.id}/ezsfinder.txt 2> {errorfile}"
  )
  if (pathtest != 0):
    await ctx.reply(
      f"Something went wrong with the percent command. Please check for any typos you might have had.\nThe error code is {pathtest}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  output = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read()
  solverate = (output[output.find("success"):output.find("success") +
                      20].split()[2])
  output = output.splitlines()
  doprint = False
  with open(f"__userdata/{ctx.author.id}/failqueues.txt",
            "w") as failqueuesfile:
    failqueuesfile.write("Fail queues:\n")
    accum = ""
    for i in output:
      if (i == "" and doprint):
        break
      if (doprint):
        accum += i + "\n"
      if ("Fail pattern" in i):
        doprint = True
    failqueuesfile.write(accum)
  await ctx.reply(
    f"The chance of solving the setup is {solverate}.",
    file=discord.File(f"__userdata/{ctx.author.id}/failqueues.txt"))


@bot.command(aliases=["mins", "min"])
async def minimals(ctx, fumen=None, queue=None, clear=4, saves=None):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (queue == None):
    await ctx.reply("Please provide a queue")
    return

  errorfile = f"__userdata/{ctx.author.id}/error.txt"
  covercsv = f"__userdata/{ctx.author.id}/cover.csv"
  outputfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"

  if (saves == None or saves.upper() == "ALL"):
    pathtest = await system(
      ctx,
      f"java -jar sfinder.jar path -f csv -k pattern --tetfu {fumen} --patterns {queue} --clear {clear} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -o {covercsv} > {outputfile} 2> {errorfile}"
    )

    if (pathtest != 0):
      await ctx.reply(
      f"Something went wrong with the path command. Please check for any typos you might have had.\nThe error code is {pathtest}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
      return

    await system(ctx, f"sfinder-minimal {covercsv} > {outputfile}")
    await system(
      ctx,
      f"python3 true_minimal.py > {outputfile}")
    minimallink = open(outputfile).read().splitlines()[1]
    await ctx.reply(f"The normal minimals are {minimallink}")
  else:
    pathtest = await system(
      ctx,
      f"java -jar sfinder.jar path -t {fumen} -p {queue} -f csv -k pattern -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} --clear {clear} --output __userdata/{ctx.author.id}/path.csv > __userdata/{ctx.author.id}/ezsfinder.txt 2> {errorfile}"
    )
    if (pathtest != 0):
      await ctx.reply(
        f"Something went wrong with the path command. Please check for any typos you might have had.\nThe error code is {pathtest}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
      return
    filtertest = await system(
      ctx,
      f'python3 sfinder-saves.py filter -w "{saves}" -p {queue} -f __userdata/{ctx.author.id}/path.csv > __userdata/{ctx.author.id}/ezsfinder.txt 2> {errorfile}'
    )
    if (filtertest != 0):
      await ctx.reply(
      f"Something went wrong running sfinder-saves.py. It does not take queue input as liberally as sfinder, so make sure to put commas. Please check for any typos you might have had.\nThe error code is {pathtest}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
      return

    pieces = saves.replace("||", "")
    output = open(
      f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()
    await ctx.reply(f"The save {pieces} minimals are {output[-1]}")
  remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")


def resize_image_with_median(image, new_width, new_height):
  # Resize the image to the desired width and height
  resized_image = image.resize((new_width, new_height))

  # Get the size of the resized image
  resized_width, resized_height = resized_image.size

  # Calculate the grid size based on the number of rows and columns
  grid_width = image.width // resized_width
  grid_height = image.height // resized_height

  # Create a new image to store the median RGB values
  median_image = Image.new("RGB", (resized_width, resized_height))

  # Iterate through each pixel in the resized image
  for y in range(resized_height):
    for x in range(resized_width):
      # Calculate the grid boundaries
      left = x * grid_width
      upper = y * grid_height
      right = (x + 1) * grid_width
      lower = (y + 1) * grid_height

      # Get the grid square from the original image
      grid_square = image.crop((left, upper, right, lower))

      # Get the RGB values for each pixel in the grid square
      grid_pixels = list(grid_square.getdata())

      # Calculate the median RGB values
      median_rgb = tuple(
        int(sum(channel) / len(channel)) for channel in zip(*grid_pixels))

      # Assign the median RGB values to the corresponding pixel in the median image
      median_image.putpixel((x, y), median_rgb)

  return median_image


def encode(text):
  text = '\n'.join(text[i:i + 10] for i in range(0, len(text), 10))
  tetrisfield = Field(field=text, garbage="__________")
  page = Page(field=tetrisfield)
  return (pyencode([page]))


def decode(fumen):
  decode_pages = pydecode(fumen)
  return '\n'.join(decode_pages[0].field.string().splitlines()[:-1])


catimages = {}
for i in "IOSZJLTX_":
  catimages[i] = Image.open(f"cat images/cat{i}.png")


def toimage(fumen):
  board = decode(fumen)
  board = [[i for i in j] for j in board.splitlines()]

  fumenimage = Image.new("RGB", (len(board[0]) * 32, len(board) * 32), "black")

  for rownumber, row in enumerate(board):
    for columnnumber, piece in enumerate(row):
      if (not piece == "_"):
        fumenimage.paste(catimages[piece], (columnnumber * 32, rownumber * 32))
  image_buffer = io.BytesIO()
  fumenimage.save(image_buffer, format="PNG")
  image_buffer.seek(0)
  discord_file = discord.File(image_buffer, filename="image.png")

  return discord_file


def create_mode_image(original_image, new_width, new_height):
  # Open the original image

  # Calculate the cell size based on the new resolution
  cell_width = original_image.width // new_width
  cell_height = original_image.height // new_height

  # Create a new image for storing the cell mode RGB values
  new_image = Image.new("RGB", (new_width, new_height))

  # Iterate over each cell in the new image
  for row in range(new_height):
    for col in range(new_width):
      # Define the boundaries of the current cell in the original image
      left = col * cell_width
      upper = row * cell_height
      right = left + cell_width
      lower = upper + cell_height

      # Crop the original image to the current cell
      cell_image = original_image.crop((left, upper, right, lower))

      # Calculate the mode RGB value of the cell
      mode_rgb = cell_image.convert("RGB").getcolors(cell_width * cell_height)
      mode_rgb = max(mode_rgb, key=lambda x: x[0])[1]

      # Set the mode RGB value in the new image
      new_image.putpixel((col, row), mode_rgb)

  return new_image


bot.command()
async def textfumen(ctx, *, textfumen=None):
  if textFumen == None:
    ctx.reply("Attach a text fumen")
  textfumen = textfumen.upper()
  textfumen = textfumen.replace("\n", "")
  textfumen = ''.join([i if i in "IOSZJLTX_" else "" for i in textfumen])
  if (len(textfumen) % 10 != 0):
    await ctx.reply(
      f"Board length must be multiple of 10. The current length is {len(textfumen)}"
    )
  await ctx.reply(encode(textfumen))
  return


def get_closest_piece(rgb_value, preset, pieceSet="normal"):
  closest_piece = None
  closest_distance = float('inf')

  pieces = preset[pieceSet]

  # Iterate through each Tetris piece and its RGB value
  for piece, piece_rgb in pieces.items():
    # Calculate the Euclidean distance between the RGB values
    distance = math.sqrt(
      sum((c1 - c2)**2 for c1, c2 in zip(rgb_value, piece_rgb)))

    # Update the closest piece if the distance is smaller
    # If the piece is void, make the margin slightly smaller
    if piece == '_' or piece == 'X':
      if distance * 1.1 < closest_distance:
        closest_distance = distance * 1.1
        closest_piece = piece
      continue

    if distance < closest_distance:
      closest_distance = distance
      closest_piece = piece

  return closest_piece


@bot.command()
async def tofumen(ctx, preset=None):
  if preset != None:
    folderpath = f"rgbShorthands/{preset.lower()}.json"
    if not path.exists(folderpath):
      await ctx.reply(
        "Preset does not exist (check help for the full list or ping epic to add)\n"
      )
      return
    open(f"__userdata/{ctx.author.id}/toFumenRGB.json",
         'w').write(open(folderpath).read())

  if not path.exists(f"__userdata/{ctx.author.id}/toFumenRGB.json"):
    folderpath = f"rgbShorthands/fumen.json"
    open(f"__userdata/{ctx.author.id}/toFumenRGB.json",
         'w').write(open(folderpath).read())

  # Check if an image is attached
  if len(ctx.message.attachments) == 0:
    await ctx.reply("No image found.")
    return

  # Get the image attachment
  attachment = ctx.message.attachments[0]

  try:
    image_bytes = await attachment.read()
    image_io = io.BytesIO(image_bytes)

    image = Image.open(image_io)
    width, height = image.size
    new_width = 10
    new_height = round(new_width * height / width)

    # Resize the image
    # image = create_mode_image(image, new_width, new_height)
    image = image.resize((new_width, new_height), Image.NEAREST)
    # Convert the image to a Tetris field
    pieces = json.loads(
      open(f"__userdata/{ctx.author.id}/toFumenRGB.json").read())

    field = ''
    for y in range(new_height):
      line = ""
      for x in range(new_width):
        pixel = image.getpixel((x, y))
        closest_piece = get_closest_piece(pixel, pieces)
        line += closest_piece

      if not '_' in line:
        line = ""
        for x in range(new_width):
          pixel = image.getpixel((x, y))
          closest_piece = get_closest_piece(pixel, pieces, "cleared")
          line += closest_piece

      field += line + '\n'

    # Send the field back to the user
    await ctx.reply("```\n" + field + "```" + "\n" +
                    encode(field.replace("\n", "")))

  except Exception:
    await ctx.reply("An error occurred while processing the image.")
    traceback.print_exc()


def remove_duplicates(file_name):
  unique_lines = set()

  # Read file and collect unique lines
  with open(file_name, 'r') as file:
    for line in file:
      line = line.strip()
      if line not in unique_lines:
        unique_lines.add(line)

  # Rewrite unique lines to the file
  with open(file_name, 'w') as file:
    file.write('\n'.join(unique_lines))


def generate_permutations(bag, permutation_length):
  elements = list(bag)

  if elements and elements[0] == '^':
    # Negate the list of elements
    elements = [p for p in "IOSZJLT" if p not in elements[1:]]
  else:
    elements = elements[
      1:-1] if elements[0] == '[' and elements[-1] == ']' else elements

  permutations = [[]]
  result = set()

  # Generate all permutations of the given length
  for i in range(permutation_length):
    permutations = [
      p + [e] for p in permutations for e in elements if e not in p
    ]

  # Convert each permutation back to a string and add to the result set
  for p in permutations:
    result.add(''.join(p))

  # Convert the result set to a list and return it
  return list(result)


def combine_lists(lists):
  if not lists:
    return []

  result = []

  def combine(index, current):
    if index == len(lists):
      result.append(''.join(current))
      return
    for i in range(len(lists[index])):
      combine(index + 1, current + [lists[index][i]])

  combine(0, [])
  return result


def countpieces(string):
  count = 0
  if ("^" in string):
    string = [p for p in "IOSZJLT" if p not in string[string.index("^"):]]
  for char in string:
    if (char in "IOSZJLT"):
      count += 1
  return count


def queuesplit(string):
  bagmode = False
  result = []
  for char in string:
    char = char.upper() if char in "ioszjlt" else char
    if (not bagmode and char in "IOSZJLT"):
      result.append(char)
    if (char == "[" or char == "*"):
      temp = ""
      bagmode = True
    if (bagmode == True):
      temp += char
    if (char == "!" or char in "0123456789"):
      result.append(temp)
      bagmode = False

  result = ','.join(result)
  return result


def sfinder_all_permutations(input_str):
  input_str = queuesplit(input_str)
  inputs = input_str.split(',')

  # Generate all permutations for each input
  permutations = []
  for input_str in inputs:
    input_str = input_str.replace("^", "[^]").replace(
      "!", "p" + str(countpieces(input_str)))
    if (not "p" in input_str):
      input_str += "p1"
    bag_with_brackets, permutation_length = input_str.split('p')
    if not permutation_length:
      permutation_length = 1

    bag = bag_with_brackets.replace('*', '[IOSZJLT]').replace('[', '').replace(
      ']', '').upper()

    permutations.append(generate_permutations(bag, int(permutation_length)))

  return combine_lists(permutations)


def holdsfinderqueues(queue):
  properhold = set()
  for i in sfinder_all_permutations(queue):
    [properhold.add(j) for j in hold_reorders(i)]

  return (list(properhold))


@bot.command()
async def special_minimals(ctx,
                           fumen=None,
                           queue=None,
                           clear=4,
                           minimal_type="tss"):
  if (fumen == None or queue == None):
    await ctx.reply("You have to specify a fumen and a queue")

  if minimal_type == "quad":
    minimal_type = "tetris"

  errorfile = f"__userdata/{ctx.author.id}/error.txt"

  sfindercommand = await system(
    ctx,
    f"java -jar sfinder.jar path -t {fumen} -p {queue} --clear {clear} -K kicks/{get_kicks(ctx)}.properties --split yes -d {get_180(ctx)} -o __userdata/{ctx.author.id}/path > __userdata/{ctx.author.id}/ezsfinder.txt 2> {errorfile}"
  )

  if (sfindercommand != 0):
    await ctx.reply(
        f"Something went wrong with the path command. Please check for any typos you might have had.\nThe error code is {sfindercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  with open(f'__userdata/{ctx.author.id}/path_unique.html',
            encoding="utf-8") as f:
    html = f.read()

  soup = BeautifulSoup(html, 'html.parser')
  links = []
  for link in soup.findAll('a'):
    links.append(link.get('href'))
    allfumen = links[1:]

  with open(f"__userdata/{ctx.author.id}/coverfield.txt", "w") as file:
    for i in allfumen:
      file.write(i)
      file.write("\n")

  remove_duplicates(f"__userdata/{ctx.author.id}/coverfield.txt")

  covercommand = await system(
    ctx,
    f"java -jar sfinder.jar cover -p {queue} -M {minimal_type} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -fp __userdata/{ctx.author.id}/coverfield.txt -o __userdata/{ctx.author.id}/tempcover.csv > __userdata/{ctx.author.id}/ezsfinder.txt 2> {errorfile}"
  )

  if (covercommand != 0):
    await ctx.reply(
        f"Something went wrong with the cover command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  await system(
    ctx,
    f"python3 cover-to-path.py --csv-path __userdata/{ctx.author.id}/tempcover.csv > __userdata/{ctx.author.id}/ezsfinder.txt"
  )

  await system(
    ctx,
    f"sfinder-minimal __userdata/{ctx.author.id}/tempcover_to_path.csv > __userdata/{ctx.author.id}/ezsfinder.txt"
  )
  await system(
    ctx, f"python3 true_minimal.py > __userdata/{ctx.author.id}/ezsfinder.txt")
  trueminimallink = open(
      f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()[-1]
  await ctx.reply(f"Your {minimal_type} minimals are {trueminimallink}")

  #remove(f"__userdata/{ctx.author.id}/coverfield.txt")
  #remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")
  #remove(f"__userdata/{ctx.author.id}/tempcover.csv")
  #remove(f"__userdata/{ctx.author.id}/tempcover_to_path.csv")

@bot.command()
async def special_cover(ctx, fumen=None, queue=None, clear=4, minimal_type="tss"):
  if (fumen == None or queue == None):
    await ctx.reply("You have to specify a fumen and a queue")

  errorfile = f"__userdata/{ctx.author.id}/error.txt"

  sfindercommand = await system(
    ctx,
    f"java -jar sfinder.jar path -t {fumen} -p {queue} --clear {clear} -K kicks/{get_kicks(ctx)}.properties --split yes -d {get_180(ctx)} -o __userdata/{ctx.author.id}/path > __userdata/{ctx.author.id}/ezsfinder.txt 2> {errorfile}"
  )

  if (sfindercommand != 0):
    await ctx.reply(
        f"Something went wrong with the path command. Please check for any typos you might have had.\nThe error code is {sfindercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  with open(f'__userdata/{ctx.author.id}/path_unique.html',
            encoding="utf-8") as f:
    html = f.read()

  soup = BeautifulSoup(html, 'html.parser')
  links = []
  allfumen = None
  for link in soup.findAll('a'):
    links.append(link.get('href'))
    allfumen = links[1:]

  if allfumen == None:
    await ctx.reply("No solutions at all! 0% cover.")
    return;

  with open(f"__userdata/{ctx.author.id}/coverfield.txt", "w") as file:
    for i in allfumen:
      file.write(i)
      file.write("\n")

  remove_duplicates(f"__userdata/{ctx.author.id}/coverfield.txt")

  covercommand = await system(
    ctx,
    f"java -jar sfinder.jar cover -p {queue} -M {minimal_type} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -fp __userdata/{ctx.author.id}/coverfield.txt -o __userdata/{ctx.author.id}/tempcover.csv> __userdata/{ctx.author.id}/ezsfinder.txt 2> {errorfile}"
  )

  if (covercommand != 0):
    await ctx.reply(
        f"Something went wrong with the cover command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  allqueues = 0
  setupcover = 0
  failqueues = open(f"__userdata/{ctx.author.id}/coverfailqueues.txt", "w")

  coverfile = open(f"__userdata/{ctx.author.id}/tempcover.csv").read().splitlines()[1:]
  for cover in coverfile:
    allqueues += 1
    coverage = cover.split(",")[1:]
    coverqueue = cover.split(",")[0]
    coverage = any([True if i == "O" else False for i in coverage])
    if (coverage):
      setupcover += 1
    else:
      failqueues.write(coverqueue)
      failqueues.write("\n")
  failqueues.close()

  await ctx.reply(
    f"The coverage is {setupcover}/{allqueues} ({setupcover/allqueues*100}%)")
  if (setupcover != allqueues):
    await ctx.send("Fail queues")
    await ctx.send(
      file=discord.File(f"__userdata/{ctx.author.id}/coverfailqueues.txt"))

@bot.command(aliases=["congruents"])
async def congruent(ctx, fumen=None, queue=None, blueGarbage=""):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (queue == None):
    await ctx.reply("Please provide a queue")
    return

  if blueGarbage.lower() == "true":
    await system(
      ctx,
      f"node convertalltoblue.js {fumen} > __userdata/{ctx.author.id}/tempblued.txt"
    )
  else:
    await system(
      ctx,
      f"node converttoblue.js {fumen} > __userdata/{ctx.author.id}/tempblued.txt"
    )
  blued = open(f"__userdata/{ctx.author.id}/tempblued.txt").read().replace(
    "\n", "")
  blued = encode(blued)

  await system(
    ctx,
    f"java -jar sfinder.jar setup --fill I --tetfu {blued} --patterns {queue} -d {get_180(ctx)} -K kicks/tetrio180.properties -fo csv --output __userdata/{ctx.author.id}/tempsetup.csv > setupoutput.txt 2> __userdata/{ctx.author.id}/error.txt"
  )

  try:
    allfumens = [
      i.split(",")[0] for i in open(
        f"__userdata/{ctx.author.id}/tempsetup.csv").read().splitlines()[1:]
    ]
  except FileNotFoundError:
    await ctx.reply("Error on sfinder!",
                    file=discord.File(f"__userdata/{ctx.author.id}/error.txt"))
    return

  if (allfumens == []):
    await ctx.reply(
      "Looks like there were no congruents. If all the blocks are garbage, make sure to enable the garbage parameter."
    )
    return

  allfumens = join(allfumens)[0]
  try:
    await ctx.reply(make_tiny("https://fumen.zui.jp/?" + allfumens))
  except:
    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "w") as file:
      file.write("https://fumen.zui.jp/?" + allfumens)

    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "rb") as file:
      await ctx.reply("Congruents (tinyurl failed):",
                      file=discord.File(file, "result.txt"))

    remove(f"__userdata/{ctx.author.id}/tiny_error.txt")

  remove(f"__userdata/{ctx.author.id}/tempblued.txt")
  remove(f"__userdata/{ctx.author.id}/tempsetup.csv")


@bot.command()
async def cover(ctx, fumens=None, queue=None, mode="normal", mirror="no", kicks="jstris180"):
  if (fumens == None):
    await ctx.reply("Please provide fumens")
    return
  elif (queue == None):
    await ctx.reply("Please provide a queue")
    return

  errorfile = f"__userdata/{ctx.author.id}/error.txt"

  gluedfumens = fumensplit([fumens])
  fumens = []
  for i in gluedfumens:
    fumens.append(glue(unglue(i)))

  fumens = " ".join(fumens)

  covercommand = await system(
    ctx,
    f"java -jar sfinder.jar cover -t \"{fumens}\" -p {queue} -K kicks/{kicks}.properties -d {get_180(ctx)} -M {mode} -m {mirror.lower()} --output __userdata/{ctx.author.id}/tempcover.csv  __userdata/{ctx.author.id}/tempcover.csv > __userdata/{ctx.author.id}/tempcover.txt 2> {errorfile}"
  )

  if (covercommand != 0):
    await ctx.reply(
        f"Something went wrong with the cover command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  allqueues = 0
  setupcover = 0
  failqueues = open(f"__userdata/{ctx.author.id}/coverfailqueues.txt", "w")

  coverfile = open(
    f"__userdata/{ctx.author.id}/tempcover.csv").read().splitlines()[1:]
  for cover in coverfile:
    allqueues += 1
    coverage = cover.split(",")[1:]
    coverqueue = cover.split(",")[0]
    coverage = any([True if i == "O" else False for i in coverage])
    if (coverage):
      setupcover += 1
    else:
      failqueues.write(coverqueue)
      failqueues.write("\n")
  failqueues.close()

  await ctx.reply(
    f"The coverage is {setupcover}/{allqueues} ({setupcover/allqueues*100}%)")
  if (setupcover != allqueues):
    await ctx.send("Fail queues")
    await ctx.send(
      file=discord.File(f"__userdata/{ctx.author.id}/coverfailqueues.txt"))

  remove(f"__userdata/{ctx.author.id}/coverfailqueues.txt")
  remove(f"__userdata/{ctx.author.id}/tempcover.csv")


@bot.command()
async def setup_set_score(ctx, 
                          fumens=None, # a single fumen with pages of setups
                          setup_queue=None, 
                          solution_queue=None, 
                          clear=4,
                          initial_b2b="false",
                          b2b_bonus=0,
                          initial_combo=0,
                          kicks="jstris180"):
  if (fumens == None):
    await ctx.reply("Please provide fumens")
    return
  elif (setup_queue == None):
    await ctx.reply("Please provide a setup queue")
    return
  elif (solution_queue == None):
    await ctx.reply("Please provide a solution queue")
    return

  errorfile = f"__userdata/{ctx.author.id}/error.txt"

  fumens = fumensplit([fumens]) # fumens is now a list of single page fumens
  gluedfumens = []
  for i in fumens:
    gluedfumens.append(glue(unglue(i)))

  gluedfumens = " ".join(gluedfumens)

  covercommand = await system(
    ctx,
    f"java -jar sfinder.jar cover -t \"{gluedfumens}\" -p {setup_queue} -K kicks/{kicks}.properties -d {get_180(ctx)} --output __userdata/{ctx.author.id}/tempcover.csv  __userdata/{ctx.author.id}/tempcover.csv > __userdata/{ctx.author.id}/tempcover.txt 2> {errorfile}"
  )

  if (covercommand != 0):
    await ctx.reply(
        f"Something went wrong with the cover command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  allqueues = 0
  setupcover = 0

  coverfile = open(
    f"__userdata/{ctx.author.id}/tempcover.csv").read().splitlines()[1:]
  for cover in coverfile:
    allqueues += 1
    coverage = cover.split(",")[1:]
    coverage = any([True if i == "O" else False for i in coverage])
    if (coverage):
      setupcover += 1

  await ctx.reply(
    f"The coverage of all setups is {setupcover}/{allqueues} ({setupcover/allqueues*100}%)")
  
  solution_queue = solution_queue.replace("*!", "*p7")

  with open(f"__userdata/{ctx.author.id}/queuefeed.txt", "w") as queuefeed:
    queuefeed.write("\n".join(holdsfinderqueues(solution_queue)))

  setup_scores = []
  for index, fumen in enumerate(fumens): # score all setups
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar path -t {fumen} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/path.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )
    if (scorecommand != 0):
      await ctx.reply(
        f"Something went wrong with the score command. Please check for any typos you might have had.\nThe error code is {scorecommand}. 137 is out of memory and tends to be the most common.",
        file=discord.File("scoreerror.txt"))
      return
    await system(
      ctx,
      f"node avg_score_ezsfinderversion.js queue={solution_queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} game={get_kicks(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
    score = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()
    for v, i in enumerate(score):
      if ("average_covered_score" in i):
        score_percentage = int(score[v + 1].split(": ")[1][:-1]) / int(
          score[-1]) * 100
        withpcscore = round(float(i.split(": ")[1][:-1]), 2)
        average_score = round(
          withpcscore / int(score[-1]) * int(score[v + 1].split(": ")[1][:-1]),
          2)
        setup_scores.append(average_score)

        await ctx.send(
          f"**Setup {index}: Factoring in pc chance ({score_percentage}%), the average score is {average_score}**"
        )
        remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")
        break


  allqueues = 0
  total_score = 0
  for cover in coverfile:
    allqueues += 1
    coverage = cover.split(",")[1:]
    is_covered = any([True if i == "O" else False for i in coverage])
    if (is_covered):
      total_score += max(score for score, condition in zip(setup_scores, coverage) if condition == "O")
  
  await ctx.send(
          f"**Average priority score: {total_score / allqueues}**"
        )
    
  
  remove(f"__userdata/{ctx.author.id}/queuefeed.txt")
  remove(f"__userdata/{ctx.author.id}/tempcover.csv")



@bot.command(aliases=[":3"])
async def imageofacat(ctx):
  response = requests.get("https://api.thecatapi.com/v1/images/search")
  data = response.json()
  image_url = data[0]['url']
  embed = discord.Embed(title="", color=0xFFA500)
  embed.set_image(url=image_url)

  await ctx.reply(embed=embed)


@bot.command()
async def congruent_cover(ctx,
                          fumens=None,
                          queue=None,
                          mode="normal",
                          mirror="no",
                          blueGarbage="boykisser >:3"):
  if (fumens == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (queue == None):
    await ctx.reply("Please provide a queue")
    return

  errorfile = f"__userdata/{ctx.author.id}/error.txt"
  print(fumens)
  fumens = fumensplit([fumens])
  unglued_fumens = []

  for fumen in fumens:
    if blueGarbage.lower() == "true":
      await system(
        ctx,
        f"node convertalltoblue.js {fumen} > __userdata/{ctx.author.id}/tempblued.txt"
      )
    else:
      await system(
        ctx,
        f"node converttoblue.js {fumen} > __userdata/{ctx.author.id}/tempblued.txt"
      )
    blued = open(f"__userdata/{ctx.author.id}/tempblued.txt").read().replace(
      "\n", "")
    blued = encode(blued)

    await system(
      ctx,
      f"java -jar sfinder.jar setup --fill I --tetfu {blued} --patterns {queue} -d {get_180(ctx)} -K kicks/tetrio180.properties -fo csv --output __userdata/{ctx.author.id}/tempsetup.csv > setupoutput.txt 2> {errorfile}"
    )

    try:
      unglued_fumens.extend([
        i.split(",")[0] for i in open(
          f"__userdata/{ctx.author.id}/tempsetup.csv").read().splitlines()[1:]
      ])
    except FileNotFoundError:
      await ctx.reply("Error on sfinder!", file=discord.File(errorfile))
      return

  if mirror.lower() == "yes":
    mfumens = []
    for fumen in unglued_fumens:
      mfumen = flip([fumen])
      mfumen = decode(mfumen[0])
      mfumen = "\n".join(mfumen)
      mfumen = mfumen[::2]
      mfumens.append(mfumen)

    outputfumen = []
    for mfumen in mfumens:
      outputfumen.append(
        Page(Field(field=mfumen, garbage="__________")))

    fumens = [*fumensplit([pyencode(outputfumen)]), *unglued_fumens]
  else:
    fumens = unglued_fumens

  if not fumens:
    await ctx.reply("No congruents!")
    return

  fumens = glue(unglue(fumens))
  fumens = ' '.join(fumens)

  covercommand = await system(
    ctx,
    f'java -jar sfinder.jar cover -t "{fumens}" -p {queue} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -M {mode} --output __userdata/{ctx.author.id}/tempcover.csv > __userdata/{ctx.author.id}/tempcover.txt 2> {errorfile}'
  )

  if (covercommand != 0):
    await ctx.reply(
        f"Something went wrong with the cover command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.", file=discord.File(errorfile))
    return

  allqueues = 0
  setupcover = 0
  failqueues = open(f"__userdata/{ctx.author.id}/coverfailqueues.txt", "w")

  coverfile = open(
    f"__userdata/{ctx.author.id}/tempcover.csv").read().splitlines()[1:]
  for cover in coverfile:
    allqueues += 1
    coverage = cover.split(",")[1:]
    coverqueue = cover.split(",")[0]
    coverage = any([True if i == "O" else False for i in coverage])
    if (coverage):
      setupcover += 1
    else:
      failqueues.write(coverqueue)
      failqueues.write("\n")

  unglued_fumens = []
  with open(f"__userdata/{ctx.author.id}/tempcover.txt", "r") as f:
    for i in f:
      if ("fumen.zui.jp" in i):
        coverfumen = i.split("fumen.zui.jp/?")[1]
        coverpercent = float(i.split("%")[0])
        if coverpercent > 0: # for removes non tsd/tss/tet/etc. solutions
          unglued_fumens.append(unglue(coverfumen))

  failqueues.close()

  await system(
    ctx,
    f"python3 cover-to-path.py --csv-path __userdata/{ctx.author.id}/tempcover.csv > __userdata/{ctx.author.id}/ezsfinder.txt"
  )

  await system(
    ctx,
    f"sfinder-minimal __userdata/{ctx.author.id}/tempcover_to_path.csv > __userdata/{ctx.author.id}/ezsfinder.txt"
  )
  await system(
    ctx, f"python3 true_minimal.py > __userdata/{ctx.author.id}/ezsfinder.txt")
  trueminimallink = open(
    f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()[-1]

  output = ""

  output += (
    f"The coverage is {setupcover}/{allqueues} ({round(setupcover/allqueues*100, 2)}%)\n"
  )

  allfumens = join(unglued_fumens)[0]
  altmode = (mode == "normal") if "" else mode
  try:
    output += (f"All {altmode} congruents: " + make_tiny("https://fumen.zui.jp/?" + allfumens) + "\n")
  except:
    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "w") as file:
      file.write("https://fumen.zui.jp/?" + allfumens)

    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "rb") as file:
      await ctx.send("Congruents (tinyurl failed):",
                     file=discord.File(file, "result.txt"))

    remove(f"__userdata/{ctx.author.id}/tiny_error.txt")

  output += (f"Your {mode} minimals are {trueminimallink}\n")

  if (setupcover != allqueues):
    await ctx.send("Fail queues", file=discord.File(f"__userdata/{ctx.author.id}/coverfailqueues.txt"))

  await ctx.reply(output)

  remove(f"__userdata/{ctx.author.id}/tempblued.txt")
  remove(f"__userdata/{ctx.author.id}/coverfailqueues.txt")
  remove(f"__userdata/{ctx.author.id}/tempcover.csv")


@bot.command()
async def saves(ctx, fumen=None, queue=None, clear=4, *, saves=None):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
  elif (queue == None):
    await ctx.reply("Please provide a queue")

  errorfile = f"__userdata/{ctx.author.id}/error.txt"

  sfindercommand = await system(
    ctx,
    f"java -jar sfinder.jar path -f csv -k pattern -t {fumen} -p {queue} --clear {clear} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} --output __userdata/{ctx.author.id}/temppath.csv > __userdata/{ctx.author.id}/ezsfinder.txt 2> {errorfile}"
  )
  if (sfindercommand != 0):
    await ctx.reply(
      f"Something went wrong with the sfinder command. Please check for any typos you might have had.\nThe error code is {sfindercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  if (saves == None):
    filtertest = await system(
      ctx,
      f"python3 sfinder-saves.py percent -p {queue} -f __userdata/{ctx.author.id}/temppath.csv -a > __userdata/{ctx.author.id}/tempsaves.txt 2> {errorfile}"
    )
  else:
    saves = saves.upper()
    filtertest = await system(
      ctx,
      f'python3 sfinder-saves.py percent -p {queue} -f __userdata/{ctx.author.id}/temppath.csv -w "{saves}" > __userdata/{ctx.author.id}/tempsaves.txt 2> {errorfile}'
    )

  if (filtertest != 0):
    await ctx.reply(
      f"Something went wrong with the sfinder-saves.py. Please check for any typos you might have had.\nThe error code is {filtertest}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  output = open(f"__userdata/{ctx.author.id}/tempsaves.txt").read()
  await ctx.reply(output)


def convert_csv(input_file, output_file):
  csv_file = open(input_file, 'r')
  csv_data = csv.reader(csv_file)
  rows = list(csv_data)[1:]

  queues_set = set()
  solutions_map = {}
  for row in rows:
    queue = row[0]
    queues_set.add(queue)
    if row[4] == '':
      continue
    solutions = row[4].split(';')
    for solution in solutions:
      if solution not in solutions_map:
        solutions_map[solution] = set([queue])
      else:
        solutions_map[solution].add(queue)

  solutions_list = list(solutions_map.keys())
  data = []
  for queue in queues_set:
    temp = [
      'O'
      if solutions_map[solution] and queue in solutions_map[solution] else 'X'
      for solution in solutions_list
    ]
    temp.insert(0, queue)
    data.append(temp)

  content = "sequence," + ','.join(solutions_list)

  for row in data:
    content += "\n" + ','.join(row)

  with open(output_file, 'w') as file:
    file.write(content)

@bot.command()
async def score(ctx,
                fumen=None,
                queue=None,
                clear=4,
                initial_b2b="false",
                b2b_bonus=0,
                initial_combo=0,
                field_file=None):
  if (fumen == None or queue == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  queue = queue.replace("*!", "*p7")

  with open(f"__userdata/{ctx.author.id}/queuefeed.txt", "w") as queuefeed:
    queuefeed.write("\n".join(holdsfinderqueues(queue)))

  if (not "FILE:" in fumen):
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar path -t {fumen} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/path.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )
  else:
    file = fumen.split("FILE:")[1]
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar cover -fp {file} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/cover.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )

  if (scorecommand != 0):
    await ctx.reply(
      f"Something went wrong with the score command. Please check for any typos you might have had.\nThe error code is {scorecommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File("scoreerror.txt"))
    return

  if (not "FILE:" in fumen):
    await system(
      ctx,
      f"node avg_score_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} game={get_kicks(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  else:
    await system(
      ctx,
      f"node avg_score_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} fileName=output/cover.csv fileType=cover > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  score = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()
  printingscores = True

  runningaccum = 0
  allspecial = "```\n"

  for v, i in enumerate(score):
    if (i == "{"):
      printingscores = False
    if (printingscores):
      specialcount = int(i.split(": ")[1])
      specialtype = i.split(": ")[0]
      allqueues = int(score[-1])
      runningaccum += specialcount
      allspecial += (
        f"There are {specialcount}/{allqueues} ({round(specialcount/allqueues * 100, 3)}%) queues where {specialtype} is the optimal solve \n"
      )
    if ("average_covered_score" in i):
      if (allspecial != "```\n"):
        allspecial += f"In total, there are {runningaccum}/{allqueues} ({round(runningaccum/allqueues * 100, 3)}%) queues where you have extra scoring"
        allspecial += "\n```"
        await ctx.reply(allspecial)
      else:
        await ctx.reply("There is no extra scoring")

      score_percentage = int(score[v + 1].split(": ")[1][:-1]) / int(
        score[-1]) * 100
      withpcscore = round(float(i.split(": ")[1][:-1]), 2)
      average_score = round(
        withpcscore / int(score[-1]) * int(score[v + 1].split(": ")[1][:-1]),
        2)

      await ctx.send(
        f"**On average, when the setup has a perfect clear, you would score {withpcscore} points.**"
      )
      await ctx.send(
        f"**Factoring in pc chance ({score_percentage}%), the average score is {average_score}**"
      )

      remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")
      remove(f"__userdata/{ctx.author.id}/queuefeed.txt")
      break

@bot.command()
async def score_allspin(ctx,
                fumen=None,
                queue=None,
                clear=4,
                initial_b2b="false",
                b2b_bonus=0,
                initial_combo=0,
                field_file=None):
  if (fumen == None or queue == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  queue = queue.replace("*!", "*p7")

  with open(f"__userdata/{ctx.author.id}/queuefeed.txt", "w") as queuefeed:
    queuefeed.write("\n".join(holdsfinderqueues(queue)))

  if (not "FILE:" in fumen):
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar path -t {fumen} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/path.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )
  else:
    file = fumen.split("FILE:")[1]
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar cover -fp {file} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/cover.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )

  if (scorecommand != 0):
    await ctx.reply(
      f"Something went wrong with the score command. Please check for any typos you might have had.\nThe error code is {scorecommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File("scoreerror.txt"))
    return

  if (not "FILE:" in fumen):
    await system(
      ctx,
      f"node avg_score_allspin_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} game={get_kicks(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  else:
    await system(
      ctx,
      f"node avg_score_allspin_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} fileName=output/cover.csv fileType=cover > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  score = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()
  printingscores = True

  runningaccum = 0
  allspecial = "```\n"

  for v, i in enumerate(score):
    if (i == "{"):
      printingscores = False
    if (printingscores):
      specialcount = int(i.split(": ")[1])
      specialtype = i.split(": ")[0]
      allqueues = int(score[-1])
      runningaccum += specialcount
      allspecial += (
        f"There are {specialcount}/{allqueues} ({round(specialcount/allqueues * 100, 3)}%) queues where {specialtype} is the optimal solve \n"
      )
    if ("average_covered_score" in i):
      if (allspecial != "```\n"):
        allspecial += f"In total, there are {runningaccum}/{allqueues} ({round(runningaccum/allqueues * 100, 3)}%) queues where you have extra scoring"
        allspecial += "\n```"
        await ctx.reply(allspecial)
      else:
        await ctx.reply("There is no extra scoring")

      score_percentage = int(score[v + 1].split(": ")[1][:-1]) / int(
        score[-1]) * 100
      withpcscore = round(float(i.split(": ")[1][:-1]), 2)
      average_score = round(
        withpcscore / int(score[-1]) * int(score[v + 1].split(": ")[1][:-1]),
        2)

      await ctx.send(
        f"**On average, when the setup has a perfect clear, you would score {withpcscore} points.**"
      )
      await ctx.send(
        f"**Factoring in pc chance ({score_percentage}%), the average score is {average_score}**"
      )

      remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")
      remove(f"__userdata/{ctx.author.id}/queuefeed.txt")
      break

@bot.command()
async def allspin_pres_chance(ctx,
                fumen=None,
                queue=None,
                clear=4):
  if (fumen == None or queue == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  queue = queue.replace("*!", "*p7")

  with open(f"__userdata/{ctx.author.id}/queuefeed.txt", "w") as queuefeed:
    queuefeed.write("\n".join(holdsfinderqueues(queue)))

  if (not "FILE:" in fumen):
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar path -t {fumen} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/path.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )
  else:
    file = fumen.split("FILE:")[1]
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar cover -fp {file} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/cover.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )

  if (scorecommand != 0):
    await ctx.reply(
      f"Something went wrong with the command. Please check for any typos you might have had.\nThe error code is {scorecommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File("scoreerror.txt"))
    return

  if (not "FILE:" in fumen):
    await system(
      ctx,
      f"node allspin_pres_chance.js queue={queue} game={get_kicks(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  else:
    await system(
      ctx,
      f"node allspin_pres_chance.js queue={queue} fileName=output/cover.csv fileType=cover > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  score = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()

  msg = "```js\n"
  in_msg = False
  for v, i in enumerate(score):
    if "{" in i:
      in_msg = True
    if in_msg:
      msg += i
  msg += "```"
  await ctx.reply(msg, file=discord.File(f"__userdata/{ctx.author.id}/ezsfinder.txt"))

  remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")
  remove(f"__userdata/{ctx.author.id}/queuefeed.txt")

@bot.command()
async def allspin_sol_finder(ctx,
                fumen=None,
                queue=None,
                clear=4):
  if (fumen == None or queue == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  queue = queue.replace("*!", "*p7")
  if "!" in queue or "p" in queue:
    await ctx.reply(f"bro this command is specifically for 1 queue")
    return

  with open(f"__userdata/{ctx.author.id}/queuefeed.txt", "w") as queuefeed:
    queuefeed.write("\n".join(holdsfinderqueues(queue)))

  if (not "FILE:" in fumen):
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar path -t {fumen} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/path.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )
  else:
    file = fumen.split("FILE:")[1]
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar cover -fp {file} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/cover.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )

  if (scorecommand != 0):
    await ctx.reply(
      f"Something went wrong with the command. Please check for any typos you might have had.\nThe error code is {scorecommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File("scoreerror.txt"))
    return

  if (not "FILE:" in fumen):
    await system(
      ctx,
      f"node allspin_sol_finder.js queue={queue} game={get_kicks(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  else:
    await system(
      ctx,
      f"node allspin_sol_finder.js queue={queue} fileName=output/cover.csv fileType=cover > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  score = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()

  msg = ""
  for v, i in enumerate(score):
      msg += i

  await ctx.reply(msg)

  remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")
  remove(f"__userdata/{ctx.author.id}/queuefeed.txt")



@bot.command()
async def score_minimals(ctx,
                         testfumen=None,
                         testqueue=None,
                         clear=4,
                         initial_b2b="false",
                         b2bendbonus=0,
                         initial_combo=0,
                         fuzzymargin=200,
                         weights=None):
  if (testfumen == None or testqueue == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  pathfile = f"__userdata/{ctx.author.id}/path.csv"
  holdoutputfile = f"__userdata/{ctx.author.id}/holdyescover.csv"
  noholdoutputfile = f"__userdata/{ctx.author.id}/holdavoidcover.csv"
  outputfile = f"__userdata/{ctx.author.id}/scorecover.csv"
  outputpathfile = f"__userdata/{ctx.author.id}/scorepath.csv"
  solutionsfeedfile = f"__userdata/{ctx.author.id}/solutionsfeed.txt"
  queuefeedfile = f"__userdata/{ctx.author.id}/holdreorders.txt"
  trueminimallink = f"__userdata/{ctx.author.id}/minimallink.txt"

  await system(
    ctx,
    f"java -jar sfinder.jar path -t {testfumen} -p {testqueue} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} --split yes --clear {clear} --output {pathfile} -f csv -k pattern > ezsfinder.txt"
  )

  convert_csv(pathfile, holdoutputfile)
  solutions = open(holdoutputfile).read().splitlines()[0].split(",")[1:]

  holddata = holdsfinderqueues(testqueue)

  with open(queuefeedfile, "w") as file:
    file.write("\n".join(holddata))

  with open(solutionsfeedfile, "w") as file:
    file.write("\n".join(solutions))

  await system(
    ctx,
    f"java -jar sfinder.jar cover -fp {solutionsfeedfile} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -pp {queuefeedfile} --hold avoid -o {noholdoutputfile}> ezsfinder.txt"
  )
  await system(
    ctx,
    f"java -jar sfinder.jar cover -fp {solutionsfeedfile} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -p {testqueue} -o {holdoutputfile} > ezsfinder.txt"
  )

  if (weights == None):
    scoretest = await system(
      ctx,
      f"node scoremins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile}"
    )
  elif (weights.upper() == "DPC"):
    scoretest = await system(
      ctx,
      f"node scoremins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile} save_weights=4726.378,4495.700,4454.710,4454.710,4255.940,4255.940,4135.546"
    )
  else:
    scoretest = await system(
      ctx,
      f"node scoremins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile} save_weights={weights}"
    )

  if (scoretest != 0):
    await ctx.reply(
      f"Something went wrong with the score command. Please check for any typos you might have had.\nThe error code is {scoretest}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  await system(
    ctx,
    f'python3 cover-to-path.py --csv-path "{outputfile}" --output-file-path "{outputpathfile}"'
  )

  await system(ctx, f"sfinder-minimal {outputpathfile}")
  await system(ctx, f"python3 true_minimal.py > {trueminimallink}")
  link = open(trueminimallink).read().splitlines()[-1]
  await ctx.reply(f"Your score minimals is {link}")

@bot.command()
async def extra_minimals(ctx,
                         testfumen=None,
                         testqueue=None,
                         clear=4,
                         initial_b2b="false",
                         b2bendbonus=0,
                         initial_combo=0,
                         fuzzymargin=200,
                         weights=None):
  if (testfumen == None or testqueue == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  pathfile = f"__userdata/{ctx.author.id}/path.csv"
  holdoutputfile = f"__userdata/{ctx.author.id}/holdyescover.csv"
  noholdoutputfile = f"__userdata/{ctx.author.id}/holdavoidcover.csv"
  outputfile = f"__userdata/{ctx.author.id}/scorecover.csv"
  outputpathfile = f"__userdata/{ctx.author.id}/scorepath.csv"
  solutionsfeedfile = f"__userdata/{ctx.author.id}/solutionsfeed.txt"
  queuefeedfile = f"__userdata/{ctx.author.id}/holdreorders.txt"
  trueminimallink = f"__userdata/{ctx.author.id}/minimallink.txt"

  await system(
    ctx,
    f"java -jar sfinder.jar path -t {testfumen} -p {testqueue} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} --split yes --clear {clear} --output {pathfile} -f csv -k pattern > ezsfinder.txt"
  )

  convert_csv(pathfile, holdoutputfile)
  solutions = open(holdoutputfile).read().splitlines()[0].split(",")[1:]

  holddata = holdsfinderqueues(testqueue)

  with open(queuefeedfile, "w") as file:
    file.write("\n".join(holddata))

  with open(solutionsfeedfile, "w") as file:
    file.write("\n".join(solutions))

  await system(
    ctx,
    f"java -jar sfinder.jar cover -fp {solutionsfeedfile} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -pp {queuefeedfile} --hold avoid -o {noholdoutputfile}> ezsfinder.txt"
  )
  await system(
    ctx,
    f"java -jar sfinder.jar cover -fp {solutionsfeedfile} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -p {testqueue} -o {holdoutputfile} > ezsfinder.txt"
  )

  if (weights == None):
    scoretest = await system(
      ctx,
      f"node extramins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile}"
    )
  elif (weights.upper() == "DPC"):
    scoretest = await system(
      ctx,
      f"node extramins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile} save_weights=4726.378,4495.700,4454.710,4454.710,4255.940,4255.940,4135.546"
    )
  else:
    scoretest = await system(
      ctx,
      f"node extramins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile} save_weights={weights}"
    )

  if (scoretest != 0):
    await ctx.reply(
      f"Something went wrong with the score command. Please check for any typos you might have had.\nThe error code is {scoretest}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  await system(
    ctx,
    f'python3 cover-to-path.py --csv-path "{outputfile}" --output-file-path "{outputpathfile}"'
  )

  await system(ctx, f"sfinder-minimal {outputpathfile}")
  await system(ctx, f"python3 true_minimal.py > {trueminimallink}")
  link = open(trueminimallink).read().splitlines()[-1]
  await ctx.reply(f"Your extra minimals is {link}")


@bot.command()
async def score_allspin_minimals(ctx,
                         testfumen=None,
                         testqueue=None,
                         clear=4,
                         initial_b2b="false",
                         b2bendbonus=0,
                         initial_combo=0,
                         fuzzymargin=200,
                         weights=None):
  if (testfumen == None or testqueue == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  pathfile = f"__userdata/{ctx.author.id}/path.csv"
  holdoutputfile = f"__userdata/{ctx.author.id}/holdyescover.csv"
  noholdoutputfile = f"__userdata/{ctx.author.id}/holdavoidcover.csv"
  outputfile = f"__userdata/{ctx.author.id}/scorecover.csv"
  outputpathfile = f"__userdata/{ctx.author.id}/scorepath.csv"
  solutionsfeedfile = f"__userdata/{ctx.author.id}/solutionsfeed.txt"
  queuefeedfile = f"__userdata/{ctx.author.id}/holdreorders.txt"
  trueminimallink = f"__userdata/{ctx.author.id}/minimallink.txt"

  await system(
    ctx,
    f"java -jar sfinder.jar path -t {testfumen} -p {testqueue} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} --split yes --clear {clear} --output {pathfile} -f csv -k pattern > ezsfinder.txt"
  )

  convert_csv(pathfile, holdoutputfile)
  solutions = open(holdoutputfile).read().splitlines()[0].split(",")[1:]

  holddata = holdsfinderqueues(testqueue)

  with open(queuefeedfile, "w") as file:
    file.write("\n".join(holddata))

  with open(solutionsfeedfile, "w") as file:
    file.write("\n".join(solutions))

  await system(
    ctx,
    f"java -jar sfinder.jar cover -fp {solutionsfeedfile} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -pp {queuefeedfile} --hold avoid -o {noholdoutputfile}> ezsfinder.txt"
  )
  await system(
    ctx,
    f"java -jar sfinder.jar cover -fp {solutionsfeedfile} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -p {testqueue} -o {holdoutputfile} > ezsfinder.txt"
  )

  if (weights == None):
    scoretest = await system(
      ctx,
      f"node scoremins_allspin.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2B={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile}"
    )
  elif (weights.upper() == "DPC"):
    scoretest = await system(
      ctx,
      f"node scoremins_allspin.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile} save_weights=4726.378,4495.700,4454.710,4454.710,4255.940,4255.940,4135.546"
    )
  else:
    scoretest = await system(
      ctx,
      f"node scoremins_allspin.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile} save_weights={weights}"
    )

  if (scoretest != 0):
    await ctx.reply(
      f"Something went wrong with the score command. Please check for any typos you might have had.\nThe error code is {scoretest}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  await system(
    ctx,
    f'python3 cover-to-path.py --csv-path "{outputfile}" --output-file-path "{outputpathfile}"'
  )

  await system(ctx, f"sfinder-minimal {outputpathfile}")
  await system(ctx, f"python3 true_minimal.py > {trueminimallink}")
  link = open(trueminimallink).read().splitlines()[-1]
  await ctx.reply(f"Your score minimals is {link}")


def evenchecker(num):
  return "EOvdedn"[num % 2::2]


def pcLine(total, highestPCLine):
  if total % 2 == 1:
    return "N/A"
  elif total % 4 == 0:
    return f"Line {math.ceil(highestPCLine / 2) * 2}"
  else:
    return f"Line {math.ceil((highestPCLine - 1) / 2) * 2 + 1}"


@bot.command()
async def parity(ctx, fumen=None):
  if (fumen == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  checkerboard = rowparity = columnar = total = 0
  highestPCLine = -1

  fumen = decode(fumen).splitlines()

  for rowindex, row in enumerate(fumen):
    for columnindex, block in enumerate(row):  # +1 for 1-indexed
      if (block != "_"):
        if (columnindex % 2 == 0):
          columnar += 1
        if (rowindex % 2 == 0):
          rowparity += 1
        if ((columnindex + rowindex) % 2 == 0):
          checkerboard += 1
        total += 1
        highestPCLine = rowindex + 1

  await ctx.reply(
    f"``` Total minos: {total}\n Next Available PC: {pcLine(total, highestPCLine)}\n Horizontal parity: {evenchecker(rowparity)}\n Vertical parity: {evenchecker(columnar)}\n Checkerboard parity: {(evenchecker(checkerboard))}```"
  )


#sorry man im testing something


@bot.command()
async def calibrate(ctx, preset=None):
  # Apply preset
  if preset != None:
    folderpath = f"rgbShorthands/{preset.lower()}.json"
    if not path.exists(folderpath):
      await ctx.reply(
        "Game preset does not exist (check help for the full list or ping epic to add)\n"
        + folderpath)
      return

    open(f"__userdata/{ctx.author.id}/toFumenRGB.json",
         'w').write(open(folderpath).read())
    await ctx.reply("Success!")
    return

  # Check if an image is attached
  if len(ctx.message.attachments) == 0:
    await ctx.reply("No image found.")
    return

  # Get the image attachment
  attachment = ctx.message.attachments[0]

  try:
    image_bytes = await attachment.read()
    image_io = io.BytesIO(image_bytes)

    image = Image.open(image_io)
    width, height = image.size
    new_width = 9
    new_height = 2

    # Resize the image
    image = image.resize((new_width, new_height), Image.NEAREST)

    # Add rgb values into dictionary

    pieces = dict()
    order = "SZLJTIOX_"
    for x in range(len(order)):
      pixel = image.getpixel((x, 1))
      pieces[order[x]] = pixel

    clearedPieces = dict()
    order = "SZLJTIOX"
    for x in range(len(order)):
      pixel = image.getpixel((x, 0))
      clearedPieces[order[x]] = pixel

    # Send the values back to the user
    message = "Pieces:\n```\n"
    for key in pieces.keys():
      message += f"{key}: {pieces.get(key)}\n"

    message += "\n```Cleared Line Pieces:\n```\n"
    for key in clearedPieces.keys():
      message += f"{key}: {clearedPieces.get(key)}\n"
    message += "\n```"

    await ctx.reply(message)

    # Write to file
    full = dict()
    full["normal"] = pieces
    full["cleared"] = clearedPieces
    with open(f"__userdata/{ctx.author.id}/toFumenRGB.json",
              'w') as convert_file:
      convert_file.write(json.dumps(full))

  except Exception:
    await ctx.reply("An error occurred while processing the image.")
    traceback.print_exc()

  # I did not write a single full line of code here but it works sooooo


@bot.command(aliases=["cc"])
async def currentcommands(ctx):
  if not running_commands:
    await ctx.reply("No commands are running right now")
    return

  message = "```\n"
  for i in running_commands:
    message += f"{i['user']}: " + i["name"] + "\n"
  message += "```"
  await ctx.reply(message)


@bot.command(aliases=["killmycommands", "kill", "k"])
async def killmyprocesses(ctx, id=None):
  kill_id = int(ctx.author.id)

  if id != None:
    if not bot_admin(ctx):
      ctx.reply("You do not have permission to kill other people's commands")
      return
    kill_id = int(id)

  for process in running_commands:
    print(f"{kill_id}, {process['user']}")
    if (kill_id == int(process['user'])):
      await ctx.send(f"`{process['name']}` killed")
      try:
        running_commands.remove(process)
      except:
        pass
      process['process'].kill()
  await ctx.reply(
    f"All processes owned by <@!{kill_id}> have been killed. Note that whatever command they were running will probably error."
  )


@bot.command()
async def togray(ctx, fumen):
  fumen = decode(fumen)
  fumen = re.sub("[SZJLTIO]", "X", fumen)
  fumen = re.sub("\n", "", fumen)
  fumen = encode(fumen)
  await ctx.reply(fumen)


tspintypes = {"TSM": 1, "TSS": 1, "TSD": 2, "TST": 3}


@bot.command()
async def spincover(ctx, fumen=None, queue=None, minimal_type="TSS"):
    if (fumen == None):
        await ctx.reply("Please provide a fumen")
        return
    elif (queue == None):
        await ctx.reply("Please provide a queue")
        return
    elif (not minimal_type.upper() in tspintypes):
        await ctx.reply("The type must be either TSM, TSS, TSD or TST.")
        return

    spinfile = f"__userdata/{ctx.author.id}/tempspin.csv"
    queuefeedfile = f"__userdata/{ctx.author.id}/tempfield.txt"
    coverfile = f"__userdata/{ctx.author.id}/cover.csv"
    coveroutputfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
    covertopathfile = f"__userdata/{ctx.author.id}/cover-to-path.csv"
    tempfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
    errorfile = f"__userdata/{ctx.author.id}/error.txt"
    mepfile = f"__userdata/{ctx.author.id}/mepfile.txt"

    is_mep = False
    if "{" in queue:
        is_mep = True

    mepqueue = extendPieces([queue])
    with open(mepfile, "w") as extendedfile:
        accum = ""
        for i in mepqueue:
            accum += i + "\n"
        extendedfile.write(accum)

    spincommand = await system(ctx, f"java -jar sfinder.jar spin -t {fumen} -p {queue} --format csv --split yes -o {spinfile} -c {tspintypes[minimal_type.upper()]} > {tempfile} 2> {errorfile}")

    if (spincommand != 0):
        await ctx.reply(f"Something went wrong with the spin command. Please check for any typos you might have had.\nThe error code is {spincommand}. 137 is out of memory and tends to be the most common.", file=discord.File(errorfile))
        return

    spins = open(spinfile, encoding="utf-8").read().splitlines()
    allspins = ""
    for spin in spins[1:]:
        spin = spin.split(",")
        allspins += spin[0] + "\n"

    with open(queuefeedfile, "w") as fieldinput:
        fieldinput.write(allspins)

    if not is_mep:
        print()
        covercommand = await system(ctx, f"java -jar sfinder.jar cover -fp {spinfile} -p {queue} --kicks kicks/jstris180.properties -d {get_180(ctx)} -o {coverfile} -M {minimal_type} > {coveroutputfile} 2> {errorfile}")
    else:
        covercommand = await system(ctx, f"java -jar sfinder.jar cover -fp {spinfile} -pp {mepfile} --kicks kicks/jstris180.properties -d {get_180(ctx)} -o {coverfile} -M {minimal_type} > {coveroutputfile} 2> {errorfile}")

    if (covercommand != 0):
        await ctx.reply(f"Something went wrong with the cover command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.", file=discord.File(errorfile))
        return

    output = ""

    setupandcover = []
    coveroutput = open(coveroutputfile).read().splitlines()
    for i in coveroutput:
        if ("fumen.zui.jp" in i):
            coverpercent = float(i.split(" %")[0])
            coverfumen = i.split("fumen.zui.jp/?")[1]
            setupandcover.append([decode(unglue(coverfumen)), coverpercent])
        elif ("OR" in i):
            totalcover = i.split(" = ")[1]
            output += f"The total coverage is {totalcover}\n"

    setupandcover.sort(key=lambda x: x[1] * -1)
    outputfumen = []

    for i in setupandcover:
        outputfumen.append(Page(Field(field=i[0], garbage="__________"), comment=str(i[1])))

    try:
        output += "All solutions: " + make_tiny("https://fumen.zui.jp/?" +
                                            pyencode(outputfumen)) + "\n"
    except:
        with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "w") as file:
            file.write("https://fumen.zui.jp/?" + pyencode(outputfumen))

        with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "rb") as file:
            await ctx.reply("All solutions: (attached as file)",
                          file=discord.File(file, "result.txt"))

        remove(f"__userdata/{ctx.author.id}/tiny_error.txt")

    await system(ctx, f"python3 cover-to-path.py --csv-path {coverfile} --output-file-path {covertopathfile} > {tempfile}")
    await system(ctx, f"sfinder-minimal {covertopathfile} > {tempfile}")
    try:
        await system(ctx, f"python3 true_minimal.py > {tempfile}")
        outputlink = open(tempfile).read().splitlines()[1]
        output += f"The minimal followup set is {outputlink}"
    except:
        pass
    await ctx.reply(output)

    remove(spinfile)
    remove(queuefeedfile)
    remove(coverfile)
    remove(coveroutputfile)
    #remove(tempfile)


@bot.command(aliases=["setupcover"])
async def setup_cover(ctx, fumen=None, queue=None, second_queue=None, minimal_type="normal", exclude="none", cover_cutoff=0.01, fill="I", margin="O"):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (queue == None):
    await ctx.reply("Please provide a setup queue")
    return
  elif (second_queue == None):
    await ctx.reply("Please provide a cover queue")
    return

  spinfile = f"__userdata/{ctx.author.id}/tempspin.csv"
  queuefeedfile = f"__userdata/{ctx.author.id}/tempfield.txt"
  coverfile = f"__userdata/{ctx.author.id}/cover.csv"
  coveroutputfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
  covertopathfile = f"__userdata/{ctx.author.id}/cover-to-path.csv"
  tempfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
  errorfile = f"__userdata/{ctx.author.id}/error.txt"
  mepfile = f"__userdata/{ctx.author.id}/mepfile.txt"

  cover_cutoff = float(cover_cutoff)

  is_mep = [False] * 2
  if "{" in queue:
    is_mep[0] = True
  if "{" in second_queue:
    is_mep[1] = True

  if not is_mep[0]:
    spincommand = await system(
      ctx,
      f"java -jar sfinder.jar setup -t {fumen} -p {queue} --format csv --split yes -o {spinfile} --fill {fill} --margin {margin} --exclude {exclude} > {tempfile} 2> {errorfile} "
    )
  else:
    mepqueue = extendPieces([queue])
    with open(mepfile, "w") as extendedfile:
      accum = ""
      for i in mepqueue:
        accum += i + "\n"
      extendedfile.write(accum)

    spincommand = await system(
      ctx,
      f"java -jar sfinder.jar setup -t {fumen} -pp {mepfile} --format csv --split yes -o {spinfile} --fill {fill} --margin {margin} --exclude {exclude} > {tempfile} 2> {errorfile} "
    )

  if (spincommand != 0):
    await ctx.reply(
    f"Something went wrong with the setup command. Please check for any typos you might have had.\nThe error code is {spincommand}. 137 is out of memory and tends to be the most common.",
    file=discord.File(errorfile))
    return

  spins = open(spinfile, encoding="utf-8").read().splitlines()

  allspins = ""
  for spin in spins[1:]:
    spin = spin.split(",")
    allspins += spin[0] + "\n"

  with open(queuefeedfile, "w") as fieldinput:
    fieldinput.write(allspins)

  covercommand = await system(
    ctx,
    f"java -jar sfinder.jar cover -fp {spinfile} -p {second_queue} --kicks kicks/jstris180.properties -d {get_180(ctx)} -o {coverfile} -M {minimal_type} > {coveroutputfile} 2> {errorfile}"
  )

  if not is_mep[1]:
    covercommand = await system(
      ctx,
      f"java -jar sfinder.jar cover -fp {spinfile} -p {second_queue} --kicks kicks/jstris180.properties -d {get_180(ctx)} -o {coverfile} -M {minimal_type} > {coveroutputfile} 2> {errorfile}"
    )
  else:
    mepqueue = extendPieces([second_queue])
    with open(mepfile, "w") as extendedfile:
      accum = ""
      for i in mepqueue:
        accum += i + "\n"
      extendedfile.write(accum)

    covercommand = await system(
      ctx,
      f"java -jar sfinder.jar cover -fp {spinfile} -pp {mepfile} --kicks kicks/jstris180.properties -d {get_180(ctx)} -o {coverfile} -M {minimal_type} > {coveroutputfile} 2> {errorfile}"
    )

  if (covercommand != 0):
    await ctx.reply(
    f"Something went wrong with the cover command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.",
    file=discord.File(errorfile))
    return

  output = ""

  setupandcover = []
  coveroutput = open(coveroutputfile).read().splitlines()
  for i in coveroutput:
    if ("fumen.zui.jp" in i):
      coverpercent = float(i.split(" %")[0])
      coverfumen = i.split("fumen.zui.jp/?")[1]
      if coverpercent >= cover_cutoff:
        setupandcover.append([decode(unglue(coverfumen)), coverpercent])
    elif ("OR  " in i):
      totalcover = i.split(" = ")[1]
      output += f"The total coverage is {totalcover}\n"

  setupandcover.sort(key=lambda x: x[1] * -1)
  #setupandcover = setupandcover[:50]
  outputfumen = []

  for i in setupandcover:
    outputfumen.append(
      Page(Field(field=i[0], garbage="__________"), comment=str(i[1])))

  try:
    output += "All solutions: " + make_tiny("https://fumen.zui.jp/?" +
                                            pyencode(outputfumen)) + "\n"
  except:
    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "w") as file:
      file.write("https://fumen.zui.jp/?" + pyencode(outputfumen))

    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "rb") as file:
      await ctx.send("All solutions (tinyurl failed):",
                     file=discord.File(file, "result.txt"))

    remove(f"__userdata/{ctx.author.id}/tiny_error.txt")

  await system(
    ctx,
    f"python3 cover-to-path.py --csv-path {coverfile} --output-file-path {covertopathfile}  > {tempfile}"
  )
  await system(ctx, f"sfinder-minimal {covertopathfile} > {tempfile}")
  await system(ctx, f"python3 true_minimal.py > {tempfile}")
  outputlink = open(tempfile).read().splitlines()[1]
  output += f"The minimal followup set is {outputlink}"
  await ctx.reply(output)

  remove(spinfile)
  remove(queuefeedfile)
  remove(coverfile)
  remove(coveroutputfile)
  remove(covertopathfile)


@bot.command()
async def catgirl(ctx):
  url = "https://drake-pi.huycao1.repl.co/catgirl/"
  # Fetch the image from the URL
  response = requests.get(url)
  response.raise_for_status(
  )  # Raise an error if the request was not successful

  # Send the image in the Discord channel
  image_bytes = response.content
  file = discord.File(io.BytesIO(image_bytes), filename="catgirl.png")
  await ctx.send(file=file)


# if the missage link is in a dm, use dm_uid to get the channel object
# dm_uid = user the dm is with
bot.command()


@bot.command()
async def jb(ctx, message_link=None, dm_uid=None):
  if not (bot_admin(ctx) or ctx.author.id ==  1050907244193136785):
    await ctx.send("I don't think jb is a command :3")
    return

  if (message_link != None):
    ids = message_link.split("/")

    if ids[4] == "@me":
      gid = -1  # in dms
    else:
      gid = int(ids[4])
    cid = int(ids[5])
    mid = int(ids[6])
    bot_id = 1112088204976341194

    guild = bot.get_guild(gid)
    if gid > 0 and guild.get_member(bot_id) == None:
      await ctx.reply("Bot is not in the linked server.")
      return

    if gid > 0:
      channel = guild.get_channel(cid)
      message = await channel.fetch_message(mid)
    else:
      dm_user = await bot.fetch_user(dm_uid)
      message = await dm_user.fetch_message(mid)

    gif = discord.File(f"jb_gifs/jb-{random.randint(1, 12)}.gif")

    await message.channel.send(f"\"{message.content}\" :nerd:",
                               file=gif,
                               reference=message,
                               mention_author=False)
    return

  if (ctx.message.reference == None):
    await ctx.reply("Please reply to the command you want to jb :D")
    return

  message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
  gif = discord.File(f"jb_gifs/jb-{random.randint(1, 12)}.gif")

  await message.channel.send(f"\"{message.content}\" :nerd:",
                             file=gif,
                             reference=message,
                             mention_author=False)

@bot.command()
async def pcnewsletterimage(ctx):
  attachments = ctx.message.attachments
  if len(attachments) != 6:
    await ctx.send(
      f"Please provide exactly 6 images. You have provided {len(attachments)}")
    return
  try:
    images = []
    for attachment in attachments:
      image_bytes = await attachment.read()
      image = Image.open(io.BytesIO(image_bytes))
      images.append(image)

    final_image = Image.open("backgroundimage.png").convert("RGB")

    def scale_image(image, row, column):
      nonlocal final_image
      current_pic = image.copy()

      w, h = current_pic.size

      if w >= h:
        current_pic = current_pic.resize(
          (int(w * 1480 / w), int(h * 1480 / w)))
      else:
        current_pic = current_pic.resize(
          (int(w * 1480 / h), int(h * 1480 / h)))

      w, h = current_pic.size

      final_image.paste(
        current_pic,
        box=(1500 * row + int((1492 - w) / 2), 1500 * column + int(
          (1492 - h) / 2)),
      )

    counter = 0
    for column in range(2):
      for row in range(3):
        scale_image(images[counter], row, column)
        counter += 1

    # Save the final image to a BytesIO buffer
    image_buffer = io.BytesIO()
    final_image.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    # Send the image as a file
    await ctx.send(file=discord.File(image_buffer, filename="collage.png"))

  except Exception as e:
    await ctx.send(f"Error creating the collage: {e}")


def get_failed_pc(pieces):
  return (pieces * 5) % 7 + 1


@bot.command()
async def weightedfails(ctx, uname=None):
  if (uname == None):
    await ctx.reply("Please provide an username")
    return

  pc_leaderboard_url = "https://jstris.jezevec10.com/PC-mode?display=5&user=" + uname
  res = requests.get(pc_leaderboard_url)

  if res.status_code != 200:
    await ctx.reply("Failed to fetch data.")
    return

  res_soup = BeautifulSoup(res.content, 'html.parser')

  table = res_soup.find('table')

  pc_nums = []
  pc_pieces = []

  for row in table.find_all('tr')[1:]:
    cols = row.find_all('td')[0].find_all('td')
    pc_nums.append(int(cols[1].text))
    pc_pieces.append(int(cols[3].text))

  fails = {x: 0 for x in range(1, 8)}
  n = len(pc_pieces)
  denom = n * (n + 1) // 2

  for (k, p) in enumerate(pc_pieces):
    fails[get_failed_pc(p)] += (n - k) / denom

  # Create the plot
  plt.bar(range(len(fails)), list(fails.values()), align='center')
  plt.xticks(range(len(fails)), list(fails.keys()))
  plt.title(f"PC Fails for User {uname}")

  # Save the plot to a file
  buffer = io.BytesIO()
  plt.savefig(buffer, format='png')
  buffer.seek(0)
  plt.close()

  # Send the file as an attachment
  await ctx.send(
    file=discord.File(buffer, filename='thanks_torchlight_for_code.png'))


@bot.command()
async def blacklist(ctx, uid=None):
  if not bot_admin(ctx):
    await ctx.reply("Insufficient permissions!")
    return
  if uid == None:
    await ctx.reply("send a user id/mention pls :D")
    return
  if uid.startswith("<@"):
    uid = uid[2:-1]

  if ("blacklist" + uid) in db.keys():
    del db["blacklist" + uid]
  else:
    db["blacklist" + uid] = "girl"

  await ctx.send(f"Blacklisted <@!{uid}> successfully!",
                 reference=ctx.message,
                 mention_author=False)


@bot.command()
async def td(ctx):
  with open("td_db.csv", "rt") as f:
    tds = list(csv.reader(f))

  choice = random.randint(0, len(tds))

  await ctx.send(f"{tds[choice][0]}",
                 reference=ctx.message,
                 file=(toimage(tds[choice][1])))


@bot.command()
async def command_blacklist(ctx, command=None):
  if ctx.guild == None:
    ctx.reply("Cannot blacklist in DMs.")
    return
  if not (bot_admin(ctx) or ctx.permissions.manage_guild):
    ctx.reply("Insufficient permissions young lad!!!!!!!")
    return
  if command == None:
    await ctx.reply("send a command name pls :D")
    return

  gid = ctx.guild.id
  key = f"command_ban{gid}{command}"

  if key in db.keys():
    del db[key]
    await ctx.send(f"Un-blacklisted `{command}` successfully!",
                   reference=ctx.message)
  else:
    db[key] = "girl"
    await ctx.send(f"Blacklisted `{command}` successfully!",
                   reference=ctx.message)

@bot.check
async def check_commands(ctx):
  if ctx.guild == None:
    key = f"command_ban{ctx.author.id}{ctx.command.qualified_name}"
  else:
    key = f"command_ban{ctx.guild.id}{ctx.command.qualified_name}"
  return not (key in db.keys())
  # return True

@bot.command(aliases=[":("])
async def angery(ctx):
  await ctx.message.remove_reaction("<a:boykisser_jumpscare:1131246599113289849>", bot.user)
  await ctx.message.add_reaction("<:ANGERY:988155325834231849>")


# bc im lazy, input as letters for now
# etc. *p7 --> *, [IOTZ]! --> IOTZ
# will likely fix later
# will give you JACK SHIT on mirrored outputs so beware
@bot.command()
async def dependencies(ctx, queue=None):
  if queue == None:
    await ctx.reply("Please add a queue.")
    return
  if queue == "*":
    queue = "IOTJLSZ"
  if len(ctx.message.attachments) == 0:
    await ctx.reply("No attachment found.")
    return

  dependencies = set()
  dep_queues = dict()
  all_patterns = ["".join(map(str, i)) for i in permutations([*queue], 2)]
  pass_queues = []
  try:
    # Get the attachment + parse
    attachment = ctx.message.attachments[0]
    file_bytes = await attachment.read()
    pass_queues = file_bytes.decode().splitlines()
  except:
    await ctx.reply("File read failed.")
    return

  # webhook = "https://discord.com/api/webhooks/1137059426537308290/V_iU9f6VZZ5OdqSKy_wDrwMZhoDp4wpIQHU4aqlhJyOnpEC1hVESkpihYOOLFGLWPAHQ"
  logging_message = ""

  def is_dependency(queue, pattern):
    for c in queue:
      if c == pattern[0]:
        return True;
      elif c == pattern[1]:
        return False;

    return false;

  for pattern in all_patterns:
    i = 0
    dep_queues[pattern] = 0

    for queue in pass_queues:
      i += 1
      if is_dependency(queue, pattern):
        dep_queues[pattern] += 1

    logging_message += f"Pattern {pattern} worked for {dep_queues[pattern]}/{len(pass_queues)} queues\n"
    if dep_queues[pattern] == len(pass_queues):
      dependencies.add(pattern)


  message = ""
  if dependencies:
    message += "Absolute dependencies: "
    for d in dependencies:
      message += f"{d[1]}>{d[0]}, "
    message = message[:-2] + "\n"

  first_count = dict.fromkeys(list(queue), 0)
  last_count = dict.fromkeys(list(queue), 0)

  for pattern, count in dep_queues.items():
    first_count[pattern[0]] += count
    last_count[pattern[1]] += count

  logging_message += "\n"
  for piece in queue:
    logging_message += f"Piece {piece} has a first count of {first_count[piece]} and a last count of {last_count[piece]}\n"

  filepath = f"__userdata/{ctx.author.id}/logging_message.txt"

  with open(filepath, "w") as file:
      file.write(logging_message)

  message += "log:"
  with open(filepath, "rb") as file:
    await ctx.send(message + "log:", file=discord.File(file, "logging_message.txt"))

  remove(filepath)


# this is like REALLY memory intensive
# like "ddos the bot until replit restarts it" intensive
# uncomment + run on an alt if you feel like annoying pc gang without consequences
# otherwise go fuck yourself
@bot.command(aliases=["setupcoverpercent", "scp"])
async def setup_cover_percent(ctx,
                      fumen=None,
                      setup_queue=None,
                      cover_queue=None,
                      percent_queue=None,
                      clear=4,
                      cover_cutoff=100.0,
                      percent_cutoff=0.01,
                      minimal_type="normal",
                      exclude="none",
                      fill="I",
                      margin="O"):
  try:
    if (fumen == None):
      await ctx.reply("Please provide a fumen")
      return
    elif (setup_queue == None):
      await ctx.reply("Please provide a setup queue")
      return
    elif (cover_queue == None):
      await ctx.reply("Please provide a cover queue")
      return
    elif (percent_queue == None):
      await ctx.reply("Please provide a percent queue")
      return

    spinfile = f"__userdata/{ctx.author.id}/tempspin.csv"
    queuefeedfile = f"__userdata/{ctx.author.id}/tempfield.txt"
    coverfile = f"__userdata/{ctx.author.id}/cover.csv"
    coveroutputfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
    covertopathfile = f"__userdata/{ctx.author.id}/cover-to-path.csv"
    tempfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
    errorfile = f"__userdata/{ctx.author.id}/error.txt"
    mepfile = f"__userdata/{ctx.author.id}/tempextended.txt"

    is_mep = [False] * 3
    if "{" in setup_queue:
      is_mep[0] = True
    if "{" in cover_queue:
      is_mep[1] = True
    if "{" in percent_queue:
      is_mep[2] = True

    if not is_mep[0]:
      spincommand = await system(
        ctx,
        f"java -jar sfinder.jar setup -t {fumen} -p {setup_queue} --format csv --split yes -o {spinfile} --fill {fill} --margin {margin} --exclude {exclude} > {tempfile} 2> {errorfile} "
      )
    else:
      mepqueue = extendPieces([setup_queue])
      with open(mepfile, "w") as extendedfile:
        accum = ""
        for i in mepqueue:
          accum += i + "\n"
        extendedfile.write(accum)

      spincommand = await system(
        ctx,
        f"java -jar sfinder.jar setup -t {fumen} -pp {mepfile} --format csv --split yes -o {spinfile} --fill {fill} --margin {margin} --exclude {exclude} > {tempfile} 2> {errorfile} "
      )

    if (spincommand != 0):
      await ctx.reply(
      f"Something went wrong with the setup command. Please check for any typos you might have had.\nThe error code is {spincommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
      return

    spins = open(spinfile, encoding="utf-8").read().splitlines()

    allspins = ""
    for spin in spins[1:]:
      spin = spin.split(",")
      allspins += spin[0] + "\n"

    with open(queuefeedfile, "w") as fieldinput:
      fieldinput.write(allspins)

    if not is_mep[1]:
      covercommand = await system(
        ctx,
        f"java -jar sfinder.jar cover -fp {spinfile} -p {cover_queue} --kicks kicks/jstris180.properties -d {get_180(ctx)} -o {coverfile} -M {minimal_type} > {coveroutputfile} 2> {errorfile}"
      )
    else:
      mepqueue = extendPieces([cover_queue])
      with open(mepfile, "w") as extendedfile:
        accum = ""
        for i in mepqueue:
          accum += i + "\n"
        extendedfile.write(accum)

      covercommand = await system(
        ctx,
        f"java -jar sfinder.jar cover -fp {spinfile} -pp {mepfile} --kicks kicks/jstris180.properties -d {get_180(ctx)} -o {coverfile} -M {minimal_type} > {coveroutputfile} 2> {errorfile}"
      )

    if (covercommand != 0):
      await ctx.reply(
      f"Something went wrong with the cover command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
      return

    output = ""

    outputdict = {} # {fumen:[cover, percent]}
    coveroutput = open(coveroutputfile).read().splitlines()
    for i in coveroutput:
      if ("fumen.zui.jp" in i):
        coverfumen = i.split("fumen.zui.jp/?")[1]
        coverpercent = float(i.split("%")[0])
        if coverpercent >= cover_cutoff: # for removes non tsd/tss/tet/etc. solutions
          outputdict[unglue(coverfumen)] = [coverpercent, 0.0]
      elif ("OR" in i):
        totalcover = i.split(" = ")[1]
        output += f"The total coverage is {totalcover}\n"

    percentfumens = {} # {grayfumen:[fumen1, fumen2...]}
    for pfumen in outputdict.keys():
      grayfumen = decode(pfumen)
      grayfumen = re.sub("[SZJLTIO]", "X", grayfumen)
      grayfumen = re.sub("\n", "", grayfumen)
      grayfumen = encode(grayfumen)

      if grayfumen in percentfumens.keys():
        percentfumens[grayfumen].append(pfumen)
      else:
        percentfumens[grayfumen] = [pfumen]

    # with open(mepfile, "w") as extendedfile:
    #   extendedfile.write(percentfumens)
    # ctx.reply(file=discord.File(mepfile))
    # raise commandKilled("Someone killed your command already!")

    if is_mep[2]:
      mepqueue = extendPieces([percent_queue])
      with open(mepfile, "w") as extendedfile:
        accum = ""
        for i in mepqueue:
          accum += i + "\n"
        extendedfile.write(accum)
    for percent_fumen, fumens in percentfumens.items():
      if not is_mep[2]:
        percentcommand = await system(
        ctx,
          f"java -jar sfinder.jar percent --tetfu {percent_fumen} --patterns {percent_queue} --clear {clear} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > {tempfile} 2> error.txt"
        )
      else:
        percentcommand = await system(
        ctx,
          f"java -jar sfinder.jar percent --tetfu {percent_fumen} -pp {mepfile} --clear {clear} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > {tempfile} 2> error.txt"
        )

      if (percentcommand != 0):
        await ctx.reply(
      f"Something went wrong with the percent command. Please check for any typos you might have had.\nThe error code is {percentcommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
        return

      p_output = open(tempfile).read() # output already exists >:(
      solverate = float(p_output[p_output.find("success"):p_output.find("success") +
                          20].split()[2][:-1])

      if solverate >= percent_cutoff:
        for pfumen in fumens:
          outputdict[pfumen][1] = solverate
      else:
        for pfumen in fumens:
          outputdict.pop(pfumen)

    outputdict = dict(sorted(outputdict.items(), key=lambda x:(x[1][0]*10000+x[1][1]), reverse=True))

    outputfumen = []
    for ofumen, data in outputdict.items():
      outputfumen.append(
        Page(Field(field=decode(ofumen), garbage="__________"), comment=f"Cover: {data[0]}%, Solve: {data[1]}%"))

    try:
      output += "All solutions: " + make_tiny("https://fumen.zui.jp/?" +
                                              pyencode(outputfumen)) + "\n"
    except:
      with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "w") as file:
        file.write("https://fumen.zui.jp/?" + pyencode(outputfumen))

      with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "rb") as file:
        await ctx.send("All solutions (tinyurl failed):",
                       file=discord.File(file, "result.txt"))

      remove(f"__userdata/{ctx.author.id}/tiny_error.txt")

    await ctx.reply(output)

    # remove(spinfile)
    # remove(queuefeedfile)
    # remove(coverfile)
    # remove(coveroutputfile)
    # remove(tempfile)
  except:
    traceback.print_exc()


@bot.command(aliases=["coverpercent", "cp"])
async def cover_percent(ctx,
                      fumens=None,
                      cover_queue=None,
                      percent_queue=None,
                      clear=4,
                      minimal_type="normal",
                      mirror="no"):
  if (fumens == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (cover_queue == None):
    await ctx.reply("Please provide a cover queue")
    return
  elif (percent_queue == None):
    await ctx.reply("Please provide a percent queue")
    return

  is_mep = [False] * 2
  if "{" in cover_queue:
    is_mep[0] = True
  if "{" in percent_queue:
    is_mep[1] = True

  if "file" in fumens.lower():
    try:
      # Get the attachment + parse
      attachment = ctx.message.attachments[0]
      file_bytes = await attachment.read()
      fumens = file_bytes.decode()
    except:
      await ctx.reply("File read failed.")
      return

  coverfile = f"__userdata/{ctx.author.id}/cover.csv"
  coveroutputfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
  covertopathfile = f"__userdata/{ctx.author.id}/cover-to-path.csv"
  tempfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
  errorfile = f"__userdata/{ctx.author.id}/error.txt"
  mepfile = f"__userdata/{ctx.author.id}/tempextended.txt"

  gluedfumens = fumensplit([fumens])
  fumens = []
  for i in gluedfumens:
    fumens.append(glue(unglue(i)))

  fumens = " ".join(fumens)

  if not is_mep[0]:
    covercommand = await system(
      ctx,
      f"java -jar sfinder.jar cover -t {fumens} -p {cover_queue} --kicks kicks/jstris180.properties -d {get_180(ctx)} -o {coverfile} -M {minimal_type} -m {mirror} > {coveroutputfile} 2> {errorfile}"
    )
  else:
    mepqueue = extendPieces([cover_queue])
    with open(mepfile, "w") as extendedfile:
      accum = ""
      for i in mepqueue:
        accum += i + "\n"
      extendedfile.write(accum)

    covercommand = await system(
      ctx,
      f"java -jar sfinder.jar cover -t {fumens} -pp {mepfile} --kicks kicks/jstris180.properties -d {get_180(ctx)} -o {coverfile} -M {minimal_type} -m {mirror} > {coveroutputfile} 2> {errorfile}"
    )

  if (covercommand != 0):
    await ctx.reply(
      f"Something went wrong with the cover command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  output = ""

  outputdict = {} # {fumen:[cover, percent, set(failqueues)]}
  coveroutput = open(coveroutputfile).read().splitlines()
  for i in coveroutput:
    if ("fumen.zui.jp" in i):
      coverfumen = i.split("fumen.zui.jp/?")[1]
      coverpercent = float(i.split(" %")[0])
      #if float(coverpercent) > 0.0: # for removes non tsd/tss/tet/etc. solutions (ADD BACK IF WANTED)
      outputdict[coverfumen] = [float(coverpercent), 0.0] # GLUED KEY
    elif ("OR" in i):
      totalcover = i.split(" = ")[1]
      output += f"The total coverage is {totalcover}\n"

  tempdict = {}
  for glued_fumen, data in outputdict.items():
    tempdict[unglue(glued_fumen)] = data
  outputdict = tempdict


  percentfumens = {} # {grayfumen:[fumen1, fumen2...]}
  for pfumen in outputdict.keys():
    grayfumen = decode(pfumen)
    grayfumen = re.sub("[SZJLTIO]", "X", grayfumen)
    grayfumen = re.sub("\n", "", grayfumen)
    grayfumen = encode(grayfumen)

    if grayfumen in percentfumens.keys():
      percentfumens[grayfumen].append(pfumen)
    else:
      percentfumens[grayfumen] = [pfumen]

  for percent_fumen, fumens in percentfumens.items():
    if not is_mep[1]:
      percentcommand = await system(
      ctx,
        f"java -jar sfinder.jar percent --tetfu {percent_fumen} --patterns {percent_queue} --clear {clear} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > {tempfile} 2> error.txt"
      )
    else:
      percentcommand = await system(
      ctx,
        f"java -jar sfinder.jar percent --tetfu {percent_fumen} -pp {mepfile} --clear {clear} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > {tempfile} 2> error.txt"
      )

    if (percentcommand != 0):
      await ctx.reply(
      f"Something went wrong with the percent command. Please check for any typos you might have had.\nThe error code is {percentcommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
      return

    p_output = open(tempfile).read() # output already exists >:(
    solverate = float(p_output[p_output.find("success"):p_output.find("success") +
                        20].split()[2][:-1])

    if solverate >= 0:
      for pfumen in fumens:
        outputdict[pfumen][1] = solverate
    else:
      for pfumen in fumens:
        outputdict.pop(pfumen)

  outputdict = dict(sorted(outputdict.items(), key=lambda x:x[1][1], reverse=True))

  outputfumen = []
  for ofumen, data in outputdict.items():
    outputfumen.append(
      Page(Field(field=decode(ofumen), garbage="__________"), comment=f"Cover: {data[0]}, Solve: {data[1]}"))

  try:
    output += "All solutions: " + make_tiny("https://fumen.zui.jp/?" +
                                            pyencode(outputfumen)) + "\n"
  except:
    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "w") as file:
      file.write("https://fumen.zui.jp/?" + pyencode(outputfumen))

    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "rb") as file:
      await ctx.send("All solutions (tinyurl failed):",
                     file=discord.File(file, "result.txt"))

    remove(f"__userdata/{ctx.author.id}/tiny_error.txt")

  await ctx.reply(output)

  remove(coverfile)
  remove(coveroutputfile)
  remove(tempfile)


@bot.command(aliases=["pc_setup", "setup_finder, setupfinder"])
async def pcsetup(ctx, *, parameters=None):
  if parameters is None:
    await ctx.reply("Parameters are missing, please set some.")
  elif "-o" in parameters:
    await ctx.reply(
      "I'm sorry, but the -o flag messes with the bot. Please don't use it.")
  elif "-lp" in parameters or "--log-path" in parameters:
    await ctx.reply(
      "I'm sorry, but the -o flag messes with the bot. Please don't use it.")
  else:
    parameters = parameters.replace('>', "")
    output_filename = f"__userdata/{ctx.author.id}/theosfinderoutput.txt"
    errorfile = f"__userdata/{ctx.author.id}/error.txt"

    lastcommand = await system(
      ctx,
      f"java -jar sfinder-pcsetup-v0.2.1.jar pcsetup {parameters} > {output_filename} 2> {errorfile}"
    )

    if (lastcommand != 0):
      await ctx.reply(
      f"Something went wrong with the setup finder. Please check for any typos you might have had.\nThe error code is {lastcommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
      return

    await ctx.reply(file=discord.File(output_filename))

    # Delete the output file
    remove(output_filename)


# Accesses ALL of db
@bot.command(aliases=["db"])
async def database(ctx, key=None):
  if not bot_admin(ctx):
    ctx.reply("Insufficient permissions young lad!!!!!!!")
    return
  if key == None:
    ctx.reply("please give a key")
    return

  if key in db.keys():
    del db[key]
    await ctx.send(f"Deleted key `{key}` successfully!",
                   reference=ctx.message)
  else:
    db[key] = "boy"
    await ctx.send(f"Added key `{key}` successfully!",
                   reference=ctx.message)


@bot.command()
async def catboy(ctx):
  url = "https://rand-image-api.beaterofall.repl.co/catboy/"
  # Fetch the image from the URL
  response = requests.get(url)
  response.raise_for_status(
  )  # Raise an error if the request was not successful

  # Send the image in the Discord channel
  image_bytes = response.content
  file = discord.File(io.BytesIO(image_bytes), filename="catboy.png")
  await ctx.send(file=file)


@bot.command(aliases=["viewdb", "vdb"])
async def view_database(ctx, prefix=None):
  if not bot_admin(ctx):
    ctx.reply("no perms?")
    return

  if prefix is None:
    await ctx.reply(db.keys())
  else:
    d = dict(filter(lambda elem : elem[0].startswith(prefix), db.items()))
    await ctx.reply(d.keys())

@bot.command()
async def mirror(ctx, fumens, append="false"):
  if fumens is None:
    ctx.reply("please attach a fumen!!!!1!!")
    return

  fumens_split = fumensplit([fumens])
  mfumens = []
  for fumen in fumens_split:
    mfumen = flip([fumen])
    mfumen = decode(*mfumen)
    mfumen = "\n".join(mfumen)
    mfumen = mfumen[::2]
    mfumens.append(mfumen)

  outputfumen = []
  for mfumen in mfumens:
    outputfumen.append(
      Page(Field(field=mfumen, garbage="__________")))


  if append.lower() == "true":
    for fumen in fumens_split:
      outputfumen.append(
        Page(Field(field=decode(fumen), garbage="__________")))

  output = "Mirror: " + make_tiny("https://fumen.zui.jp/?" + pyencode(outputfumen))
  await ctx.reply(output)

@bot.command(aliases=["path", "unique", "uniques"])
async def path_all_solutions(ctx, fumen=None, queue=None, clear=4):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (queue == None):
    await ctx.reply("Please provide a queue")
    return

  output_file = f"__userdata/{ctx.author.id}/path.txt"
  error_file = f"__userdata/{ctx.author.id}/error.txt"

  setupcommand = await system(ctx, f"java -jar sfinder.jar path --tetfu {fumen} --patterns {queue} --clear {clear} -d {get_180(ctx)} -K kicks/tetrio180.properties -o __userdata/{ctx.author.id}/path > {output_file} 2> {error_file}")

  if (setupcommand != 0):
    await ctx.reply(
    f"Something went wrong with the percent command. Please check for any typos you might have had.\nThe error code is {setupcommand}. 137 is out of memory and tends to be the most common.", file=discord.File(error_file))
    return

  with open(f"__userdata/{ctx.author.id}/path_unique.html", "r") as file:
    file_contents = file.read()
    soup = BeautifulSoup(file_contents, 'html.parser')
    link = soup.find('a')
    href = link.get('href')
    try:
      href = make_tiny(href)
      await ctx.reply(f"All Solutions: {href}")
    except:
      with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "w") as file:
        file.write(href)

      with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "rb") as file:
        await ctx.send("All solutions (tinyurl failed):",
                     file=discord.File(file, "result.txt"))

  remove(output_file)


@bot.command()
async def boykisser(ctx):
  url = "https://drake-pi.huycao1.repl.co//boykisser/"
  # Fetch the image from the URL
  response = requests.get(url)
  response.raise_for_status(
  )  # Raise an error if the request was not successful

  # Send the image in the Discord channel
  image_bytes = response.content
  file = discord.File(io.BytesIO(image_bytes), filename="boykisser.png")
  await ctx.send(file=file)


@bot.command(aliases=["100"])
async def cover_cutoff(ctx,
                      fumens=None,
                      cover_queue=None,
                      minimal_type="normal",
                      cover_cutoff=100.0):
  if (fumens == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (cover_queue == None):
    await ctx.reply("Please provide a cover queue")
    return

  spinfile = f"__userdata/{ctx.author.id}/tempspin.csv"
  queuefeedfile = f"__userdata/{ctx.author.id}/tempfield.txt"
  coverfile = f"__userdata/{ctx.author.id}/cover.csv"
  coveroutputfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
  covertopathfile = f"__userdata/{ctx.author.id}/cover-to-path.csv"
  tempfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
  errorfile = f"__userdata/{ctx.author.id}/error.txt"
  # i just copied this over from scp if you feel like sorting through them feel free
  # but like
  # do you *need* to?

  gluedfumens = fumensplit([fumens])
  fumens = []
  for i in gluedfumens:
    fumens.append(glue(unglue(i)))

  fumens = " ".join(fumens)

  covercommand = await system(
    ctx,
    f"java -jar sfinder.jar cover -t \"{fumens}\" -p {cover_queue} --kicks kicks/jstris180.properties -d {get_180(ctx)} -o {coverfile} -M {minimal_type} > {coveroutputfile} 2> {errorfile}"
  )
  if (covercommand != 0):
    await ctx.reply(
      f"Something went wrong with the percent command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  output = ""

  outputdict = {} # {fumen:cover}
  coveroutput = open(coveroutputfile).read().splitlines()
  for i in coveroutput:
    if ("fumen.zui.jp" in i):
      coverfumen = i.split("fumen.zui.jp/?")[1]
      coverpercent = float(i.split("%")[0])
      if coverpercent >= cover_cutoff: # for removes non tsd/tss/tet/etc. solutions
        outputdict[unglue(coverfumen)] = coverpercent
    # elif ("OR" in i):
    #   totalcover = i.split(" = ")[1]
    #   output += f"The total coverage is {totalcover}\n" # i dont think we really need this here


  outputdict = dict(sorted(outputdict.items(), key=lambda x:x[1], reverse=True))

  outputfumen = []
  for ofumen, cover_percent in outputdict.items():
    outputfumen.append(
      Page(Field(field=decode(ofumen), garbage="__________"), comment=f"Cover: {cover_percent}%"))

  try:
    output += "All solutions: " + make_tiny("https://fumen.zui.jp/?" +
                                            pyencode(outputfumen)) + "\n"
  except:
    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "w") as file:
      file.write("https://fumen.zui.jp/?" + pyencode(outputfumen))

    with open(f"__userdata/{ctx.author.id}/tiny_error.txt", "rb") as file:
      await ctx.send("All solutions (tinyurl failed):",
                     file=discord.File(file, "result.txt"))

    remove(f"__userdata/{ctx.author.id}/tiny_error.txt")

  await ctx.reply(output)

  remove(spinfile)
  remove(queuefeedfile)
  remove(coverfile)
  remove(coveroutputfile)
  remove(tempfile)


@bot.command()
async def clean_comments(ctx, fumens = None):
  if (fumens == None):
    await ctx.reply("Please provide a fumen")
    return

  outputfumen = []
  for fumen in fumensplit([fumens]):
    outputfumen.append(
      Page(Field(field=fumen, garbage="__________")))

  ctx.reply("All solutions: " + make_tiny("https://fumen.zui.jp/?" + pyencode(outputfumen)) + "\n")


@bot.command()
async def cover_minimals(ctx, fumens = None, queue = None, mode = "normal"):
  if (fumens == None):
    await ctx.reply("Please provide a fumen")
    return
  if (queue == None):
    await ctx.reply("Please provide a queue")
    return

  errorfile = f"__userdata/{ctx.author.id}/error.txt"

  unglued_fumens = fumens
  fumens = glue(unglue(fumensplit([fumens])))
  fumens = ' '.join(fumens)

  covercommand = await system(ctx, f'java -jar sfinder.jar cover -t "{fumens}" -p {queue} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -M {mode} --output __userdata/{ctx.author.id}/tempcover.csv > __userdata/{ctx.author.id}/tempcover.txt 2> {errorfile}')

  if (covercommand != 0):
    await ctx.reply(
      f"Something went wrong with the cover command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  allqueues = 0
  setupcover = 0
  failqueues = open(f"__userdata/{ctx.author.id}/coverfailqueues.txt", "w")

  coverfile = open(f"__userdata/{ctx.author.id}/tempcover.csv").read().splitlines()[1:]
  for cover in coverfile:
    allqueues += 1
    coverage = cover.split(",")[1:]
    coverqueue = cover.split(",")[0]
    coverage = any([True if i == "O" else False for i in coverage])
    if (coverage):
      setupcover += 1
    else:
      failqueues.write(coverqueue)
      failqueues.write("\n")
  failqueues.close()

  await system(
    ctx,
    f"python3 cover-to-path.py --csv-path __userdata/{ctx.author.id}/tempcover.csv > __userdata/{ctx.author.id}/ezsfinder.txt")

  await system(
    ctx,
    f"sfinder-minimal __userdata/{ctx.author.id}/tempcover_to_path.csv > __userdata/{ctx.author.id}/ezsfinder.txt"
  )
  await system(
    ctx, f"python3 true_minimal.py > __userdata/{ctx.author.id}/ezsfinder.txt")
  trueminimallink = open(
    f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()[-1]

  await ctx.reply(
    f"The coverage is {setupcover}/{allqueues} ({round(setupcover/allqueues*100, 2)}%)\n"
    + f"Your {mode} minimals are {trueminimallink}")

  remove(f"__userdata/{ctx.author.id}/coverfailqueues.txt")
  remove(f"__userdata/{ctx.author.id}/tempcover.csv")


@bot.command()
async def kys(ctx):
  message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
  await message.delete()

  await ctx.message.remove_reaction("<a:boykisser_jumpscare:1131246599113289849>", bot.user)
  await ctx.message.add_reaction("<:boykiller:1147003116298965093>")



@bot.command(aliases=["pp", "placepiece", "finesse"])
async def place_piece(ctx, fumen = None, game = "jstris", drop = "instant"):
  if (fumen == None):
    await ctx.reply("Please provide a fumen with operation")
    return

  output_file = f"__userdata/{ctx.author.id}/tempoutput.txt"
  errorfile = f"__userdata/{ctx.author.id}/error.txt"

  command = await system(
      ctx,
      f"node place_piece.js {fumen} {game.lower()} {drop.lower()} > {output_file} 2> {errorfile}"
    )

  if (command != 0):
    await ctx.reply(
      f"Something went wrong with the place piece script. Please check for any typos you might have had.\nThe error code is {command}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  output = open(output_file, "r").read().splitlines()
  if output == "":
    await ctx.reply("Empty file, nothing found? Tell epic pls :D")
    return

  if output[0] == "fuck you":
    await ctx.reply("No solution found! Piece is not placeable under the current conditions.")
    return

  await ctx.send(output[1])
  await catimage(ctx, output[1], 800)
  await ctx.send(output[0])

  remove(output_file)


@bot.command()
async def sudo(ctx, command, message_link=None, dm_uid=None):
  if not bot_admin(ctx):
    await ctx.send("I don't think sudo is a command :3")
    return

  if command == None:
    await ctx.reply("pls add command")
    return

  if message_link == None:
    await ctx.reply("add message link!!!")


  ids = message_link.split("/")

  if ids[4] == "@me":
    gid = -1  # in dms
  else:
    gid = int(ids[4])
  cid = int(ids[5])
  mid = int(ids[6])
  bot_id = 1112088204976341194

  guild = bot.get_guild(gid)
  if gid > 0 and guild.get_member(bot_id) == None:
    await ctx.reply("Bot is not in the linked server.")
    return

  if gid > 0:
    channel = guild.get_channel(cid)
    message = await channel.fetch_message(mid)
  else:
    dm_user = await bot.fetch_user(dm_uid)
    message = await dm_user.fetch_message(mid)

  message.content = command

  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  logging_message = f"{current_time} - {message.author.name} ({message.author.id}) ran command in \"{message.guild}\": `{message.content}`\n\n Jump url: {message.jump_url}"
  webhook = os.environ['logging_webhook']

  requests.post(webhook, json={"content": logging_message})

  await bot.process_commands(message)


@bot.command()
async def mn(ctx, uname):
  session = requests.Session()
  retry = Retry(connect=3, backoff_factor=0.5)
  adapter = HTTPAdapter(max_retries=retry)
  session.mount('http://', adapter)
  session.mount('https://', adapter)

  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'}

  pieces_vs_ppb = []

  page = ''

  while True:
    ultra_leaderboard_url = "https://jstris.jezevec10.com/ultra?display=5&user=" + uname + page

    res = session.get(ultra_leaderboard_url, headers=headers)

    if res.status_code != 200:
        print("fail")
        exit()
    res_soup = BeautifulSoup(res.content, 'html.parser')

    table = res_soup.find('table')
    runs = table.find_all('tr')[1:]
    if len(runs) < 200 and pieces_vs_ppb:
        break
    for row in runs:
        cols = row.find_all('td')[0].find_all('td')
        pieces_vs_ppb.append(
            (int(cols[2].text),        # pieces
                float(cols[3].text)))  # ppb
        local_low_score = int(cols[1].text.replace(',',''))
    page = '&page=' + str(local_low_score-1)

  plt.scatter(*zip(*pieces_vs_ppb))
  plt.title('Pieces vs PPB' + ('' if uname is None else (' for '+uname)))
  plt.xlabel('Pieces')
  plt.ylabel('PPB')

  buffer = io.BytesIO()
  plt.savefig(buffer, format='png')
  buffer.seek(0)
  plt.close()

  await ctx.reply(file=discord.File(buffer, filename='thanks_me_for_code.png'))


@bot.command()
async def best_mn(ctx, uname):
  session = requests.Session()
  retry = Retry(connect=3, backoff_factor=0.5)
  adapter = HTTPAdapter(max_retries=retry)
  session.mount('http://', adapter)
  session.mount('https://', adapter)

  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'}

  pieces_vs_ppb = []

  page = ''

  while True:
    ultra_leaderboard_url = "https://jstris.jezevec10.com/ultra?display=5&user=" + uname + page

    res = session.get(ultra_leaderboard_url, headers=headers)

    if res.status_code != 200:
        print("fail")
        exit()
    res_soup = BeautifulSoup(res.content, 'html.parser')

    table = res_soup.find('table')
    runs = table.find_all('tr')[1:]
    if len(runs) < 200 and pieces_vs_ppb:
        break
    for row in runs:
        cols = row.find_all('td')[0].find_all('td')
        pieces_vs_ppb.append(
            (int(cols[2].text),        # pieces
                float(cols[3].text)))  # ppb
        local_low_score = int(cols[1].text.replace(',',''))
    page = '&page=' + str(local_low_score-1)

  best_mn = -69.0
  best_pair = [-4, -20]
  for pieces, ppb in pieces_vs_ppb: # i cba to numpy
    mn = ppb * math.log(pieces, 10.0)**0.5
    if mn > best_mn:
      best_mn = mn
      best_pair = [ppb, pieces]

  mn = best_pair[0] * math.log(best_pair[1], 10.0)**0.5

  await ctx.reply(f"Best is {mn}mň with {best_pair[0]}PPB@{best_pair[1]}p!\n")


@bot.command(aliases=["coverscore"])
async def cover_score(ctx,
                fumens=None,
                queue=None,
                initial_b2b="false",
                b2b_bonus=0,
                initial_combo=0):
  if (fumens == None):
    await ctx.reply("Please provide fumens")
    return
  elif (queue == None):
    await ctx.reply("Please provide a queue")
    return

  errorfile = f"__userdata/{ctx.author.id}/error.txt"
  tempoutput = f"__userdata/{ctx.author.id}/ezsfinder.txt"

  gluedfumens = fumensplit([fumens])
  fumens = []
  for i in gluedfumens:
    fumens.append(glue(unglue(i)))

  fumens = " ".join(fumens)

  with open(f"__userdata/{ctx.author.id}/queuefeed.txt", "w") as queuefeed:
    accum = ""
    for i in holdsfinderqueues(queue):
      accum += i + "\n"
    queuefeed.write(accum)

  scorecommand = await system(
    ctx,
    f"java -jar sfinder.jar cover -t \"{fumens}\" -pp __userdata/{ctx.author.id}/queuefeed.txt --hold avoid -o output/cover.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > {tempoutput} 2> {errorfile}"
  )

  if (scorecommand != 0):
    await ctx.reply(
      f"Something went wrong with the score command. Please check for any typos you might have had.\nThe error code is {scorecommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  await system(
    ctx,
    f"node avg_score_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} fileName=output/cover.csv fileType=cover game={get_kicks(ctx)} > {tempoutput} 2> {errorfile}"
  )
  score = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()
  await ctx.reply(score)
  printingscores = True

  runningaccum = 0
  allspecial = "```\n"

  for v, i in enumerate(score):
    if (i == "{"):
      printingscores = False
    if (printingscores):
      specialcount = int(i.split(": ")[1])
      specialtype = i.split(": ")[0]
      allqueues = int(score[-1])
      runningaccum += specialcount
      allspecial += (
        f"There are {specialcount}/{allqueues} ({round(specialcount/allqueues * 100, 3)}%) queues where {specialtype} is the optimal solve \n"
      )
    if ("average_covered_score" in i):
      if (allspecial != "```\n"):
        allspecial += f"In total, there are {runningaccum}/{allqueues} ({round(runningaccum/allqueues * 100, 3)}%) queues where you have extra scoring"
        allspecial += "\n```"
        # await ctx.reply(allspecial) # debug
      else:
        await ctx.reply("There is no extra scoring")

      score_percentage = int(score[v + 1].split(": ")[1][:-1]) / int(
        score[-1]) * 100
      withpcscore = round(float(i.split(": ")[1][:-1]), 2)
      average_score = round(
        withpcscore / int(score[-1]) * int(score[v + 1].split(": ")[1][:-1]),
        2)

      await ctx.send(
        f"**On average, when the setup is buildable, you would score {withpcscore} points.**"
      )
      await ctx.send(
        f"**Factoring in build chance ({score_percentage}%), the average score is {average_score}**"
      )
      break

  remove(tempoutput)


@bot.command(aliases=["getpage", "page"])
async def get_page(ctx, fumen=None, index=None):
  if fumen == None:
    await ctx.reply("Please give fumen!!!")
    return
  if index == None:
    await ctx.reply("Please give an index for which page to get.")

  await ctx.reply(fumensplit([fumen])[int(index) - 1])


@bot.command(aliases=["setupcoverscore", "scs"])
async def setup_cover_score(ctx,
                      fumens=None,
                      queue=None,
                      initial_b2b="false",
                      b2b_bonus=0,
                      initial_combo=0,
                      exclude="none",
                      fill="I",
                      margin="O",):
  try:
    if (fumens == None):
      await ctx.reply("Please provide a fumen")
      return
    elif (queue == None):
      await ctx.reply("Please provide a setup queue")
      return

    setupfile = f"__userdata/{ctx.author.id}/tempsetup.csv"
    coverfile = f"__userdata/{ctx.author.id}/cover.csv"
    tempfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
    errorfile = f"__userdata/{ctx.author.id}/error.txt"
    fumenfeed = f"__userdata/{ctx.author.id}/fumenfeed.txt"

    setup_fumens = []
    fumens = fumensplit([fumens])

    for fumen in fumens:
      setupcommand = await system(
        ctx,
        f"java -jar sfinder.jar setup --fill I -t {fumen} -p {queue} -d {get_180(ctx)} -K kicks/tetrio180.properties -fo csv -o {setupfile} > {tempfile} 2> {errorfile}"
      )

      if (setupcommand != 0):
        await ctx.reply(
        f"Something went wrong with the setup command. Please check for any typos you might have had.\nThe error code is {setupcommand}. 137 is out of memory and tends to be the most common.",
        file=discord.File(errorfile))
        return

      try:
        setup_fumens.extend([
          i.split(",")[0] for i in open(setupfile).read().splitlines()[1:]
        ])
      except FileNotFoundError:
        await ctx.reply("Error on sfinder!",
                        file=discord.File(f"__userdata/{ctx.author.id}/error.txt"))
        return

    setup_fumens = glue(unglue(setup_fumens))
    fumens = []

    for fumen in setup_fumens:
      if ":" in fumen:
        print(fumen)
        fumens.extend(fumen.split(": ")[2].split(" ")) # warning: this fumen led to x outputs: f1, f2...
      else:
        fumens.append(fumen)

    fumens = np.unique(fumens)
    fumens = '\n'.join(fumens)
    with open(fumenfeed, 'w') as f:
      f.write(fumens)

    covercommand = await system(
      ctx,
      f'java -jar sfinder.jar cover -fp {fumenfeed} -p {queue} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} --hold avoid --output {coverfile} > {tempfile} 2> {errorfile}'
    )
    if (covercommand != 0):
      await ctx.reply(
      f"Something went wrong with the cover command. Please check for any typos you might have had.\nThe error code is {covercommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
      return

    await ctx.reply(file=discord.File(errorfile))

    scorecommand = await system(
      ctx,
      f"node avg_score_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} fileName={coverfile} fileType=cover > {tempfile} 2> {errorfile}"
    )
    if (scorecommand != 0):
      await ctx.reply(
      f"Something went wrong with the score command. Please check for any typos you might have had.\nThe error code is {scorecommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
      return

    score = open(tempfile).read().splitlines()
    printingscores = True

    runningaccum = 0
    allspecial = "```\n"

    for v, i in enumerate(score):
      if (i == "{"):
        printingscores = False
      if (printingscores):
        specialcount = int(i.split(": ")[1])
        specialtype = i.split(": ")[0]
        allqueues = int(score[-1])
        runningaccum += specialcount
        allspecial += (
          f"There are {specialcount}/{allqueues} ({round(specialcount/allqueues * 100, 3)}%) queues where {specialtype} is the optimal solve \n"
        )
      if ("average_covered_score" in i):
        if (allspecial != "```\n"):
          allspecial += f"In total, there are {runningaccum}/{allqueues} ({round(runningaccum/allqueues * 100, 3)}%) queues where you have extra scoring"
          allspecial += "\n```"
          await ctx.reply(allspecial)
        else:
          await ctx.reply("There is no extra scoring")

        score_percentage = int(score[v + 1].split(": ")[1][:-1]) / int(
          score[-1]) * 100
        withpcscore = round(float(i.split(": ")[1][:-1]), 2)
        average_score = round(
          withpcscore / int(score[-1]) * int(score[v + 1].split(": ")[1][:-1]),
          2)

        await ctx.send(
          f"**On average, when the setup is buildable, you would score {withpcscore} points.**"
        )
        await ctx.send(
          f"**Factoring in build chance ({score_percentage}%), the average score is {average_score}**"
        )
        break

    # remove(setupfile)
    # remove(coverfile)
    # remove(tempfile)
  except:
    traceback.print_exc()


@bot.command()
async def hot_dilf(ctx):
  dm_channel = ctx.author.dm_channel

  if dm_channel == None: # if user has not previously dmed the bot
    dm_channel = await ctx.author.create_dm()

  await ctx.reply("Check your DMs for one of our finest DILFs!")
  await dm_channel.send("In order to be born you needed:\n- 2 parents \n- 4 grandparents \n- 8 great-grandparents \n- 16 2nd great-grandparents \n- 32 3rd great-grandparents \n- 64 4th great-grandparents \n- 128 5th great-grandparents \n- 256 6th great-grandparents \n- 512 7th great-grandparents \n- 1024 8th great-grandparents \n- 2048 9th great-grandparents \nFor you to be born today from 12 previous generations, you needed a total of 4094 ancestors over the last 400 years. Think for a moment - how many struggles? How many battles? How many difficulties? How much sadness? How much happiness? How many love stories? How many expressions of hope for the future? - did your ancestors have to undergo for you to exist in this present moment, and you want to look at hot dilfs, like a femboy slut?\n# **Shame.**")


@bot.command(aliases=["spinscore", "spin_score", "catscore", "cat_score", "specialscore"])
async def special_score(ctx,
                fumen=None,
                queue=None,
                clear=4,
                initial_b2b="false",
                b2b_bonus=0,
                initial_combo=0,
                field_file=None):
  if (fumen == None or queue == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  with open(f"__userdata/{ctx.author.id}/queuefeed.txt", "w") as queuefeed:
    queuefeed.write("\n".join(holdsfinderqueues(queue)))

  if (not "FILE:" in fumen):
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar path -t {fumen} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/path.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )
  else:
    file = fumen.split("FILE:")[1]
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar cover -fp {file} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/cover.csv -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )

  if (scorecommand != 0):
    await ctx.reply(
      f"Something went wrong with the score command. Please check for any typos you might have had.\nThe error code is {scorecommand}. 137 is out of memory and tends to be the most common.",
      file=discord.File("scoreerror.txt"))
    return

  if (not "FILE:" in fumen):
    await system(
      ctx,
      f"node avg_score_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  else:
    await system(
      ctx,
      f"node avg_score_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} fileName=output/cover.csv fileType=cover catOnly=true > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  score = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()
  printingscores = True

  runningaccum = 0
  allspecial = "```\n"

  for v, i in enumerate(score):
    if (i == "{"):
      printingscores = False
    if (printingscores):
      specialcount = int(i.split(": ")[1])
      specialtype = i.split(": ")[0]
      allqueues = int(score[-1])
      runningaccum += specialcount
      allspecial += (
        f"There are {specialcount}/{allqueues} ({round(specialcount/allqueues * 100, 3)}%) queues where {specialtype} is the optimal solve \n"
      )
    if ("average_covered_score" in i):
      if (allspecial != "```\n"):
        allspecial += f"In total, there are {runningaccum}/{allqueues} ({round(runningaccum/allqueues * 100, 3)}%) queues where you have extra scoring"
        allspecial += "\n```"
        await ctx.reply(allspecial)
      else:
        await ctx.reply("There is no extra scoring")

      score_percentage = int(score[v + 1].split(": ")[1][:-1]) / int(
        score[-1]) * 100
      withpcscore = round(float(i.split(": ")[1][:-1]), 2)
      average_score = round(
        withpcscore / int(score[-1]) * int(score[v + 1].split(": ")[1][:-1]),
        2)

      await ctx.send(
        f"**On average, when the setup has a perfect clear, you would score {withpcscore} points.**"
      )
      await ctx.send(
        f"**Factoring in pc chance ({score_percentage}%), the average score is {average_score}**"
      )

      remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")
      remove(f"__userdata/{ctx.author.id}/queuefeed.txt")
      break

@bot.command(aliases=["cat_score_minimals", "catscoreminimals", "specialscoreminimals", "csm"])
async def special_score_minimals(ctx,
                         testfumen=None,
                         testqueue=None,
                         clear=4,
                         initial_b2b="false",
                         b2bendbonus=0,
                         initial_combo=0,
                         fuzzymargin=200,
                         weights=None):
  if (testfumen == None or testqueue == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  pathfile = f"__userdata/{ctx.author.id}/path.csv"
  holdoutputfile = f"__userdata/{ctx.author.id}/holdyescover.csv"
  noholdoutputfile = f"__userdata/{ctx.author.id}/holdavoidcover.csv"
  outputfile = f"__userdata/{ctx.author.id}/scorecover.csv"
  outputpathfile = f"__userdata/{ctx.author.id}/scorepath.csv"
  solutionsfeedfile = f"__userdata/{ctx.author.id}/solutionsfeed.txt"
  queuefeedfile = f"__userdata/{ctx.author.id}/holdreorders.txt"
  trueminimallink = f"__userdata/{ctx.author.id}/minimallink.txt"

  await system(
    ctx,
    f"java -jar sfinder.jar path -t {testfumen} -p {testqueue} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} --split yes --clear {clear} --output {pathfile} -f csv -k pattern > ezsfinder.txt"
  )

  convert_csv(pathfile, holdoutputfile)
  solutions = open(holdoutputfile).read().splitlines()[0].split(",")[1:]

  holddata = holdsfinderqueues(testqueue)

  with open(queuefeedfile, "w") as file:
    file.write("\n".join(holddata))

  with open(solutionsfeedfile, "w") as file:
    file.write("\n".join(solutions))

  await system(
    ctx,
    f"java -jar sfinder.jar cover -fp {solutionsfeedfile} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -pp {queuefeedfile} --hold avoid -o {noholdoutputfile}> ezsfinder.txt"
  )
  await system(
    ctx,
    f"java -jar sfinder.jar cover -fp {solutionsfeedfile} -K kicks/{get_kicks(ctx)}.properties -d {get_180(ctx)} -p {testqueue} -o {holdoutputfile} > ezsfinder.txt"
  )

  if (weights == None):
    scoretest = await system(
      ctx,
      f"node scoremins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} catOnly=True output={outputfile}"
    )
  elif (weights.upper() == "DPC"):
    scoretest = await system(
      ctx,
      f"node scoremins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile} catOnly=True save_weights=4726.378,4495.700,4454.710,4454.710,4255.940,4255.940,4135.546"
    )
  else:
    scoretest = await system(
      ctx,
      f"node scoremins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile} catOnly=True save_weights={weights}"
    )

  if (scoretest != 0):
    await ctx.reply(
      f"Something went wrong with the score command. Please check for any typos you might have had.\nThe error code is {scoretest}. 137 is out of memory and tends to be the most common.",
      file=discord.File(errorfile))
    return

  await system(
    ctx,
    f'python3 cover-to-path.py --csv-path "{outputfile}" --output-file-path "{outputpathfile}"'
  )

  await system(ctx, f"sfinder-minimal {outputpathfile}")
  await system(ctx, f"python3 true_minimal.py > {trueminimallink}")
  link = open(trueminimallink).read().splitlines()[-1]
  await ctx.reply(f"Your score minimals is {link}")

@bot.command()
async def texttofumen(ctx, *, message = None):
  if(message == None):
    await ctx.reply("Please send a fumen board")
    return

  await ctx.reply(encode(message.replace("\n", "")))

@tasks.loop(seconds=(60 * 60 * 2))
async def auto_restart():
  while running_commands:
    await asyncio.sleep(10)   # Don't kill when someone's running a command

  process = await asyncio.create_subprocess_shell("busybox reboot")
  await asyncio.wait_for(process.communicate())

  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  logging_message = f"Reset bot at {current_time} GMT+0!"
  webhook = os.environ['edp_webhook']

  requests.post(webhook, json={"content": logging_message})


bot.run(bot_token)
