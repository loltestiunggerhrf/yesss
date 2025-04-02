import os
import discord
from discord.ext import commands
from discord import app_commands
from pymongo import MongoClient
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["key_system"]
keys_collection = db["keys"]

# Discord Bot Setup
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Cooldown dictionary
user_cooldowns = {}

# Function to load keys from file
def load_keys():
    if not os.path.exists('keys.txt'):
        return []  # Return empty list if no file found
    with open('keys.txt', 'r') as file:
        return file.read().splitlines()

# Function to save keys back to file (removes used keys)
def save_keys(keys):
    with open('keys.txt', 'w') as file:
        file.write('\n'.join(keys))

# Function to move used key to `used.txt`
def move_key_to_used(key):
    with open('used.txt', 'a') as file:
        file.write(f"{key}\n")

# Slash Command: /key (Dispenses a key)
@bot.tree.command(name="key", description="Get your own keys for the scripts!")
async def key(interaction: discord.Interaction):
    user_id = interaction.user.id
    current_time = datetime.datetime.now()

    if user_id in user_cooldowns:
        last_request_time = user_cooldowns[user_id]
        if (current_time - last_request_time).total_seconds() < 86400:  # 24 hours
            await interaction.response.send_message("You can only request one key every 24 hours.", ephemeral=True)
            return

    keys = load_keys()
    if not keys:
        await interaction.response.send_message("No keys available.", ephemeral=True)
        return

    key_to_dispense = keys.pop(0)  # Get first available key
    move_key_to_used(key_to_dispense)
    save_keys(keys)  # Save remaining keys back to file
    user_cooldowns[user_id] = current_time

    await interaction.response.send_message(f"Here is your key: `{key_to_dispense}`", ephemeral=True)

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
