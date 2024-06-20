import os
import time

from dotenv import load_dotenv

import discord
from discord.ext import commands

from fc_methods import *

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
PROMPT_CMD = '/focus '
CONFIG_CMD = '/focus_cfg '

intents = discord.Intents.default()
intents.message_content = True  # Enable access to message content
bot = commands.Bot(command_prefix='!', intents=intents)


# Event listener for when the bot has connected to the server
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')


# Event listener for when a message is sent in a channel
@bot.event
async def on_message(message):
    if message.author == bot.user:  # Ignore messages sent by the bot itself
        return

    user_id = message.author.id

    if message.content is not None:
        if message.content.startswith(PROMPT_CMD):
            prompt = message.content.replace(PROMPT_CMD, '', 1)
            reply = f'So you want me to show you `{prompt}`, okay. \nPlease wait a minute...'
            await message.author.send(reply)

            print(f'Currently working on: "{prompt}"')
            start_time = time.time()
            local_copy = image_from_prompt(prompt, user_id)
            end_time = time.time()
            duration = round(end_time - start_time, 1)
            reply = f'Here is your image! \nI worked for {duration} seconds on it.'

            file = discord.File(local_copy, filename=local_copy)
            await message.reply(reply, file=file)
            os.remove(local_copy)

        if message.content.startswith(CONFIG_CMD):
            response = handle_config_request(message.content, user_id)
            await message.author.send(response)


# Run the bot with the specified token
bot.run(TOKEN)
