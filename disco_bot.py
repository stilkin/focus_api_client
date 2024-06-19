import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

from fc_methods import *

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
PROMPT_CMD = '/focus '
CONFIG_CMD = '/focus_cfg '
SERVER_IP = '192.168.178.25'
TEMP_FOLDER = 'tmp/'

intents = discord.Intents.default()
intents.message_content = True  # Enable access to message content
bot = commands.Bot(command_prefix='!', intents=intents)

focus_config = {
    'performance_selection': "Speed",
    'style_selections': [
        "Fooocus V2",
        "Fooocus Enhance",
        "Fooocus Sharp"
    ]
}


# Event listener for when the bot has connected to the server
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')


# Event listener for when a message is sent in a channel
@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    if message.content is not None:
        if message.content.startswith(PROMPT_CMD):
            prompt = message.content.replace(PROMPT_CMD, '', 1)
            reply = f'So you want me to show you `{prompt}`, okay. \nPlease wait a minute...'
            await message.reply(reply)

            print(f'Currently working on: "{prompt}"')
            local_copy = image_from_prompt(prompt)
            reply = f'Here is your image! \n'

            file = discord.File(local_copy, filename=local_copy)
            await message.reply(reply, file=file)

        if message.content.startswith(CONFIG_CMD):
            response = handle_config_request(message.content)
            await message.reply(response)


# Run the bot with the specified token
bot.run(TOKEN)
