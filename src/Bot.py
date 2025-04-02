import os
import discord
from discord.ext import commands
from pymongo import MongoClient
import datetime

# Load environment variables (e.g., MongoDB URI)
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["key_system"]
hwid_collection = db["hwids"]
keys_collection = db["keys"]

# Set up Discord bot
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True  # Needed for message handling

bot = commands.Bot(command_prefix="/", intents=intents)

# Cooldown dictionary for key requests
user_cooldowns = {}

# Function to load keys from the keys.txt file
def load_keys():
    if not os.path.exists('keys.txt'):
        return []  # Return empty list if no file found
    with open('keys.txt', 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# Function to save keys back to the keys.txt file (after redemption)
def save_keys(keys):
    with open('keys.txt', 'w') as file:
        file.write('\n'.join(keys))

# Function to move used key to the `used.txt` file
def move_key_to_used(key):
    with open('used.txt', 'a') as file:
        file.write(f"{key}\n")

# Command to redeem a key and set HWID
@bot.command()
async def redeem_key(ctx, key: str):
    """Redeem a key and associate it with a HWID"""
    user_id = ctx.author.id
    hwid = "HWID-123456789"  # This should be fetched from the user (replace with actual method)

    # Load keys from the file
    keys = load_keys()

    # Check if the key exists
    if key not in keys:
        await ctx.send("Invalid key!")
        return

    # Check if the key has been used already and is linked with a different HWID
    key_data = keys_collection.find_one({"key": key})

    if key_data and key_data["hwid"] != "None" and key_data["hwid"] != hwid:
        await ctx.send("This key has already been used on a different HWID. You cannot use it.")
        return

    # Redeem the key and set HWID in MongoDB
    keys.remove(key)
    move_key_to_used(key)  # Log the used key

    # Update the MongoDB to store HWID for the key
    keys_collection.update_one(
        {"key": key},
        {"$set": {"user_id": user_id, "hwid": hwid}},
        upsert=True
    )

    # Save remaining keys back to the file
    save_keys(keys)

    await ctx.send(f"Key `{key}` redeemed successfully with HWID `{hwid}`!")

# Command to reset HWID
@bot.command()
async def reset_hwid(ctx):
    """Reset the user's HWID"""
    user_id = ctx.author.id
    hwid_collection.update_one(
        {"user_id": user_id},
        {"$set": {"hwid": "None"}},
        upsert=True
    )
    await ctx.send("Your HWID has been reset.")

# Command to view current HWID status
@bot.command()
async def view_hwid(ctx):
    """View current HWID status"""
    user_id = ctx.author.id
    user_hwid = hwid_collection.find_one({"user_id": user_id})

    if user_hwid:
        await ctx.send(f"Your HWID is currently: {user_hwid['hwid']}")
    else:
        await ctx.send("Your HWID has not been set.")

# Command to check available keys (for admin use)
@bot.command()
async def show_keys(ctx):
    """Show all available keys"""
    keys = load_keys()
    if not keys:
        await ctx.send("No keys available.")
    else:
        await ctx.send(f"Available keys: {', '.join(keys)}")

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()  # Sync slash commands
        print(f"Synced {len(synced)} commands!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Run the bot
bot.run(TOKEN)
