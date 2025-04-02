from flask import Flask
from discord.ext import commands
import os

app = Flask(__name__)
bot = commands.Bot(command_prefix='/')

# Your bot setup goes here...

@app.route('/')
def index():
    return "If you are here you are gay"  # This will show when the page is accessed

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Make sure the port is open, change if necessary

