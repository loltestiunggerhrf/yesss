import discord
from discord.ext import commands
import datetime
import os
import subprocess  # Used to start server.py in the background

# Start the Flask web server (server.py)
server_process = subprocess.Popen(["python", "server.py"])  # Runs server.py

# Function to load keys from keys.txt
def load_keys():
    if not os.path.exists('keys.txt'):
        open('keys.txt', 'w').close()  # Create file if it doesn't exist
    with open('keys.txt', 'r') as file:
        keys = file.read().splitlines()
    return keys

# Function to save keys back to file
def save_keys(keys):
    with open('keys.txt', 'w') as file:
        file.write('\n'.join(keys))

# Function to move used keys to used.txt
def move_key_to_used(key):
    if not os.path.exists('used.txt'):
        open('used.txt', 'w').close()  
    with open('used.txt', 'a') as file:
        file.write(f"{key}\n")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Dictionary to track user cooldowns
user_cooldowns = {}

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    print('🚀 Bot and Web Server are running!')

@bot.command(name="key")
async def key(ctx):
    user_id = ctx.author.id
    current_time = datetime.datetime.now()

    # Check cooldown (24 hours)
    if user_id in user_cooldowns:
        last_request_time = user_cooldowns[user_id]
        if (current_time - last_request_time).total_seconds() < 86400:
            await ctx.author.send("⏳ You can only request one key every 24 hours.")
            return

    keys = load_keys()
    if not keys:
        await ctx.author.send("❌ No keys available.")
        return

    key_to_dispense = keys.pop(0)
    await ctx.author.send(f"🔑 Here is your key: `{key_to_dispense}`")

    move_key_to_used(key_to_dispense)
    save_keys(keys)
    user_cooldowns[user_id] = current_time

# Run the bot
bot.run('MTM1NjU2ODUxMTExMDk3NTYwMA.GSGkq0.MloSjXQm_pd6ybbzJhOHmiQwvEaKam6oygn-2I')  # Replace with your actual token
