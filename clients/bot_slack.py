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

    prompt = command['text']
    print(f'Processing command: "{prompt}"')

    expanded_prompt = expand_prompt(prompt)
    print('Expanded prompt: ', json.dumps(expanded_prompt, indent=2))

    style_arr = []
    if expanded_prompt['style'] is not None:
        style_arr = get_style_guess(json.dumps(expanded_prompt['style']))
    else:
        print('Did not get a style; defaulting to style suggestion based on whole prompt.')
        style_arr = get_style_guess(prompt)

    # generate and download an image
    prompt = json.dumps(expanded_prompt['prompt'])
    local_copy = image_from_prompt(prompt, None, style_arr)

    end_time = time.time()
    duration = round(end_time - start_time, 1)
    reply = f'Here is your image! I worked on it for {duration} seconds.'

    # Upload the file to the channel
    app.client.files_upload_v2(
        channels=command["channel_id"],
        file=local_copy,
        title=reply,
        initial_comment=expanded_prompt
    )
    os.remove(local_copy)


if __name__ == '__main__':
    handler = SocketModeHandler(app, os.environ.get('SLACK_APP_TOKEN'))
    handler.start()
