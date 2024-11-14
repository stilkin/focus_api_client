import json
import os
import sys
import time

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

sys.path.append('../')

from fooocus.fc_methods import image_from_prompt
from tools.chroma_calls import get_style_guess
from tools.or_calls import expand_prompt

load_dotenv()

# initializes Slack app
app = App(token=os.environ.get('SLACK_BOT_TOKEN'))


# Listens to incoming slash commands '/llm'
@app.command('/llm')
def handle_command(ack, say, command):
    start_time = time.time()
    ack()  # acknowledge the command request

    user_prompt = command['text']
    user_id = command['user_id']
    print(f'Processing prompt: "{user_prompt}" for user {user_id}')

    # expand prompt using LLM
    expanded_prompt = expand_prompt(user_prompt)

    # make a style guess using a vector db similarity search
    style_arr = []
    if expanded_prompt['style'] is not None:
        style_arr = get_style_guess(json.dumps(expanded_prompt['style']))
    else:
        print('Did not get a style; defaulting to style suggestion based on whole prompt.')
        style_arr = get_style_guess(user_prompt)

    expanded_prompt = json.dumps(expanded_prompt['prompt'])

    reply = (f'I have expanded your prompt to _"{expanded_prompt}"_. \n'
             f'Please note that image generation will take about 30 seconds...')
    app.client.chat_postMessage(channel=user_id, text=reply)

    # generate and download the image
    local_copy = image_from_prompt(expanded_prompt, None, style_arr)

    end_time = time.time()
    duration = round(end_time - start_time, 1)
    reply = f'Here is your image <@{user_id}>! \nI worked on it for {duration} seconds.'

    # Upload the file to the channel
    app.client.files_upload_v2(
        channels=command["channel_id"],
        file=local_copy,
        title=user_prompt,
        initial_comment=reply
    )
    os.remove(local_copy)


if __name__ == '__main__':
    handler = SocketModeHandler(app, os.environ.get('SLACK_APP_TOKEN'))
    handler.start()
