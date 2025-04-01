import os
import discord
from discord.ext import commands
import datetime

# Load the Discord bot token from the environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# If the token is not found, raise an error
if TOKEN is None:
    raise ValueError("No Discord token provided in the environment variable 'DISCORD_TOKEN'")

# Set up the bot's intents (this is required for certain features like reading message content)
intents = discord.Intents.default()
intents.message_content = True

# Create a Bot instance with the specified command prefix and intents
bot = commands.Bot(command_prefix="/", intents=intents)

# Load keys from the file (keys.txt)
def load_keys():
    if not os.path.exists('keys.txt'):
        open('keys.txt', 'w').close()  
    with open('keys.txt', 'r') as file:
        keys = file.read().splitlines()
    return keys

# Save keys back to the file (keys.txt)
def save_keys(keys):
    with open('keys.txt', 'w') as file:
        file.write('\n'.join(keys))

# Move a key to used.txt
def move_key_to_used(key):
    if not os.path.exists('used.txt'):
        open('used.txt', 'w').close()  
    with open('used.txt', 'a') as file:
        file.write(f"{key}\n")

# Dictionary to store user cooldowns
user_cooldowns = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")  # Prints the bot's username once it's logged in

# Command to handle '/key' command
@bot.command(name="key")
async def key(ctx):
    user_id = ctx.author.id
    current_time = datetime.datetime.now()

    # Check for cooldown
    if user_id in user_cooldowns:
        last_request_time = user_cooldowns[user_id]
        if (current_time - last_request_time).total_seconds() < 86400:  # 24 hours cooldown
            await ctx.author.send("You can only request one key every 24 hours.")
            return

    # Load available keys from the file
    keys = load_keys()
    if not keys:
        await ctx.author.send("No keys available.")
        return

    # Dispense a key and send it to the user
    key_to_dispense = keys.pop(0)
    await ctx.author.send(f"Here is your key: `{key_to_dispense}`")

    # Move the used key to the 'used.txt' file
    move_key_to_used(key_to_dispense)

    # Save the remaining keys
    save_keys(keys)

    # Update the cooldown for the user
    user_cooldowns[user_id] = current_time

@bot.command(name="hello")
async def hello(ctx):
    """Simple command that replies with 'Hello, world!'."""
    await ctx.send("Hello, world!")

@bot.command(name="ping")
async def ping(ctx):
    """Simple ping command to check if the bot is responding."""
    await ctx.send("Pong!")

# Run the bot using the token from the environment variable
bot.run(TOKEN)
