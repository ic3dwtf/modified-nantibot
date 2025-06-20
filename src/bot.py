from discord.ext import commands
import configparser
import discord
import asyncio
import os

cfg = configparser.ConfigParser()
cfg.read("config.ini")

token = cfg["main"]["token"]
whitelist = [int(x) for x in cfg["main"]["whitelist"].split(",")]
preset = cfg["main"]["preset"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

running_loops = set()

async def is_allowed(inter):
    if inter.user.id not in whitelist:
        await inter.response.send_message("nope", ephemeral=True)
        return False
    return True

@bot.tree.command(name="raid", description="may rate limit, no msg cap")
async def raid(inter: discord.Interaction, text: str, amount: int, delay: int):
    if not await is_allowed(inter): return
    loop_id = inter.id
    running_loops.add(loop_id)
    await inter.response.send_message(".")
    await (await inter.original_response()).delete()
    for _ in range(amount):
        if loop_id not in running_loops:
            break
        try:
            await asyncio.sleep(delay)
            await inter.followup.send(text)
        except:
            break
    running_loops.discard(loop_id)

@bot.tree.command(name="stackraid", description="raids with stack at 5 msg a time")
async def stackraid(inter: discord.Interaction, text: str, amount: int):
    if not await is_allowed(inter): return
    loop_id = inter.id
    running_loops.add(loop_id)
    await inter.response.send_message(".")
    await (await inter.original_response()).delete()
    batches = min(5, amount)
    per_batch = amount // batches
    extra = amount % batches
    for i in range(batches):
        if loop_id not in running_loops:
            break
        count = per_batch + (1 if i < extra else 0)
        messages = [text] * count
        await inter.followup.send("\n".join(messages))
    running_loops.discard(loop_id)

@bot.tree.command(name="raidpreset", description="default raid preset, uses stack")
async def raidpreset(inter: discord.Interaction):
    if not await is_allowed(inter): return
    loop_id = inter.id
    running_loops.add(loop_id)
    await inter.response.send_message(".")
    await (await inter.original_response()).delete()
    text = preset
    amount = 120
    batches = min(5, amount)
    per_batch = amount // batches
    extra = amount % batches
    for i in range(batches):
        if loop_id not in running_loops:
            break
        count = per_batch + (1 if i < extra else 0)
        messages = [text] * count
        await inter.followup.send("\n".join(messages))
    running_loops.discard(loop_id)

@bot.tree.command(name="breakloops", description="stop any running raid loops")
async def breakloops(inter: discord.Interaction):
    if not await is_allowed(inter): return
    running_loops.clear()
    await inter.response.send_message("all raids stopped")

@bot.tree.command(name="kill", description="stops bot")
async def kill(inter: discord.Interaction):
    if not await is_allowed(inter): return
    await inter.response.send_message("killed bot")
    exit()

@bot.event
async def on_ready():
    try: await bot.tree.sync()
    except Exception as e: print(f"failed to sync cmds: {e}")

os.system("cls")
bot.run(token)
