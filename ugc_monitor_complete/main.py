import os
import asyncio
import aiohttp
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
ROBLOX_COOKIE = os.getenv('_ROBLOSECURITY')

ASSETS_TO_CHECK = [
    132480395092715,  # deleted
    117812692338162   # existing
]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
deleted_assets = {}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}"
}

async def is_asset_deleted(session, asset_id):
    url = f"https://economy.roblox.com/v2/assets/{asset_id}/details"
    try:
        async with session.get(url, headers=headers) as response:
            print(f"[DEBUG] Status for {asset_id}: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"[DEBUG] Asset {asset_id} data fetched successfully: {data.get('Name')}")
                return False, data
            elif response.status == 400:
                return True, None
            else:
                return None, None
    except Exception as e:
        print(f"[ERROR] Failed to check asset {asset_id}: {e}")
        return None, None

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("👋 Bot has started and is now monitoring assets.")
    check_assets.start()

@tasks.loop(minutes=2)
async def check_assets():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ Could not find channel.")
        return

    async with aiohttp.ClientSession() as session:
        for asset_id in ASSETS_TO_CHECK:
            deleted, data = await is_asset_deleted(session, asset_id)
            if deleted is None:
                continue
            previously_deleted = deleted_assets.get(asset_id, False)
            if deleted and not previously_deleted:
                deleted_assets[asset_id] = True
                await channel.send(f"🚨 Asset **{asset_id}** has been **deleted**!")
            elif not deleted and not previously_deleted:
                deleted_assets[asset_id] = False

keep_alive()
bot.run(TOKEN)