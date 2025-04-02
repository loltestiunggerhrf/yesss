import os
import discord
from discord.ext import commands
from flask import Flask
import threading

# Initialize Flask app
app = Flask(__name__)

# Initialize Discord bot with intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# Route for Flask to bind to a port
@app.route('/')
def index():
    return "Bot is running!"

# Event: When bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Function to run Flask server in the background
def run_flask():
    app.run(host='0.0.0.0', port=5000)  # Bind to port 5000

# Run Flask server in a background thread
if __name__ == '__main__':
    # Start Flask server in a separate thread
    threading.Thread(target=run_flask).start()
    
    # Run the Discord bot
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
