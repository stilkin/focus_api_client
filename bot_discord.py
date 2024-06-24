import os
import time
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

from fc_methods import image_from_prompt, handle_config_request
from chroma_calls import cdb_query
from or_calls import expand_prompt

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
PROMPT_CMD = '/focus '
CONFIG_CMD = '/focus_cfg '

intents = discord.Intents.default()
intents.message_content = True  # Enable access to message content
bot = commands.Bot(command_prefix='!', intents=intents)


def get_style_guess(prompt):
    cdb_results = cdb_query(prompt, n_results=3)
    if cdb_results is not None and 'documents' in cdb_results:
        style_array = cdb_results['documents'][0]
        return json.dumps(style_array)
    return '["Random Style"]'


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
            reply = f'So you want me to show you `{prompt}`, okay. \nPlease hold ⏳'

            style_arr = None
            if 'go wild' in prompt:
                expanded_prompt = expand_prompt(prompt)
                style_arr = get_style_guess(json.dumps(expanded_prompt['style']))
                reply = (f'I have expanded your prompt to *{expanded_prompt['prompt']}*, '
                         f'and guesstimated your style as *{expanded_prompt['style']}*')
            elif 'style' in prompt:
                style_arr = get_style_guess(prompt)
                reply = f'I will use these styles: *{style_arr}*. Please hold ⏳'
            await message.author.send(reply)

            print(f'Currently working on: "{prompt}"')
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
