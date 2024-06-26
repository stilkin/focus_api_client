import os
import time

import discord
from discord.ext import commands
from dotenv import load_dotenv

from fc_methods import image_from_prompt, handle_config_request
from or_calls import prompt_to_style

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
            prompt = message.content.partition(' ')[2]
            reply = f'So you want me to show you `{prompt}`, okay. \nPlease hold ⏳'

            style_arr = None
            if 'style' in prompt:
                style_arr = prompt_to_style(prompt)  # TODO: rework this into basic RAG with chromaDB
                reply = f'I will use these styles: *{style_arr}*. Please hold ⏳'
            await message.author.send(reply)

            print(f'Currently working on: "{prompt}"')
            start_time = time.time()
            local_copy = image_from_prompt(prompt, user_id, style_arr)
            end_time = time.time()
            duration = round(end_time - start_time, 1)
            reply = f'Here is your image! I worked on it for {duration} seconds.'

            file = discord.File(local_copy, filename=local_copy)
            await message.reply(reply, file=file)
            os.remove(local_copy)

        if message.content.startswith(CONFIG_CMD):
            response = handle_config_request(message.content, user_id)
            await message.author.send(response)


# Run the bot with the specified token
bot.run(TOKEN)
