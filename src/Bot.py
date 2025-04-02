import os
import threading
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import server  # Import Flask server

load_dotenv()  # Load environment variables

# Start Flask web server in a background thread
threading.Thread(target=server.run, daemon=True).start()

# Create bot instance
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Function to load keys from keys.txt
def load_keys():
    if not os.path.exists("keys.txt"):
        open("keys.txt", "w").close()  # Create file if it doesn't exist
    with open("keys.txt", "r") as file:
        return file.read().splitlines()

# Function to remove used key
def remove_key(key):
    keys = load_keys()
    keys.remove(key)
    with open("keys.txt", "w") as file:
        file.write("\n".join(keys))

@bot.tree.command(name="key", description="Get your own keys for the scripts!")
async def key(interaction: discord.Interaction):
    keys = load_keys()

    if not keys:
        await interaction.response.send_message("No keys available.", ephemeral=True)
        return

    key = keys[0]  # Get first key
    remove_key(key)  # Remove key after sending

    embed = discord.Embed(
        title="Your Script Key",
        description=f"🔑 **Key:** `{key}`",
        color=discord.Color.green()
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync slash commands
    print(f"Logged in as {bot.user}")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
