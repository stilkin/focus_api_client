import json
import os
import time

import discord
from discord.ext import commands
from dotenv import load_dotenv

from fooocus.fc_methods import image_from_prompt, handle_config_request
from tools.chroma_calls import get_style_guess
from tools.or_calls import expand_prompt

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
            start_time = time.time()
            print(f'Currently working on: "{prompt}"')

            expanded_prompt = expand_prompt(prompt)
            print('Expanded prompt: ', json.dumps(expanded_prompt, indent=2))

            style_arr = None
            if expanded_prompt['style'] is not None:
                style_arr = get_style_guess(json.dumps(expanded_prompt['style']))
            else:
                style_arr = get_style_guess(prompt)  # get a style suggestion based on the whole prompt

            reply = (f'I have expanded your prompt to *{expanded_prompt['prompt']}*, '
                     f'and guesstimated your style as *{expanded_prompt['style']}*\n'
                     f'Please hold ⏳')
            await message.author.send(reply)

            # generate and download an image
            prompt = json.dumps(expanded_prompt['prompt'])
            local_copy = image_from_prompt(prompt, user_id, style_arr)

            end_time = time.time()
            duration = round(end_time - start_time, 1)
            reply = f'Here is your image! I worked on it for {duration} seconds.'

            file = discord.File(local_copy, filename=local_copy)
            await message.reply(reply, file=file)
            os.remove(local_copy)

        if message.content.startswith(CONFIG_CMD):
            command = message.content.partition(' ')[2]
            response = handle_config_request(command, user_id)
            await message.author.send(response)


# Run the bot with the specified token
bot.run(TOKEN)
