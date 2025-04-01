import os
import threading
import discord
from discord.ext import commands
import datetime

# Ensure server.py is found correctly
try:
    import server  # Import the Flask web server
except ModuleNotFoundError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Add current directory to path
    import server  # Retry importing server.py

# Load Discord bot token from environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix="/", intents=intents)

# Cooldown dictionary
user_cooldowns = {}

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Command: /key (example feature)
@bot.command(name="key")
async def key(ctx):
    user_id = ctx.author.id
    current_time = datetime.datetime.now()

    if user_id in user_cooldowns:
        last_request_time = user_cooldowns[user_id]
        if (current_time - last_request_time).total_seconds() < 86400:
            await ctx.author.send("You can only request one key every 24 hours.")
            return

    # Example response (Replace with real key logic)
    key_to_dispense = "EXAMPLE-KEY-1234"
    await ctx.author.send(f"Here is your key: `{key_to_dispense}`")

    user_cooldowns[user_id] = current_time

# Start Flask server in a separate thread
threading.Thread(target=server.run).start()

# Run the bot
bot.run(TOKEN)
