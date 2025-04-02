import os
import threading
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from pymongo import MongoClient
from dotenv import load_dotenv
import server  # Import Flask server

load_dotenv()  # Load environment variables

# Start Flask web server in a background thread
threading.Thread(target=server.run, daemon=True).start()

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["key_system"]
keys_collection = db["keys"]
hwid_collection = db["hwids"]

# Create bot instance
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Embed with buttons
class KeyRedemptionView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Redeem Key", style=discord.ButtonStyle.green)
    async def redeem_key(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Enter your key:", ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=30)
            key = msg.content.strip()

            key_data = keys_collection.find_one({"key": key})
            if not key_data:
                await interaction.followup.send("Invalid key!", ephemeral=True)
                return

            keys_collection.delete_one({"key": key})  # Remove key from DB
            hwid_collection.insert_one({"user_id": interaction.user.id, "hwid": "None"})

            await interaction.followup.send(f"Key `{key}` redeemed! You can now set your HWID.", ephemeral=True)
        except:
            await interaction.followup.send("Time expired. Please try again.", ephemeral=True)

    @discord.ui.button(label="Reset HWID", style=discord.ButtonStyle.blurple)
    async def reset_hwid(self, interaction: discord.Interaction, button: Button):
        hwid_collection.update_one(
            {"user_id": interaction.user.id},
            {"$set": {"hwid": "None"}},
            upsert=True
        )
        await interaction.response.send_message("HWID has been reset!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def panel(ctx):
    embed = discord.Embed(
        title="Key Redemption & HWID Reset",
        description="Use the buttons below to redeem your key or reset HWID.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=KeyRedemptionView())

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
