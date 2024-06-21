import json
import os

import requests
from dotenv import load_dotenv

from fc_settings import all_fc_styles

load_dotenv()
TOKEN = os.getenv('OPENROUTER_TOKEN')
APP_TAG = 'focus-client.be'
MODEL = 'anthropic/claude-3.5-sonnet'
SYS_PROMPT = (f'You are an assistant that gets requests for images, '
              'and you have to determine which visual styles match most with the request. '
              'You will be provided with a list of possible styles. '
              'You have to answer ONLY in a JSON array of strings, nothing else, '
              'and the strings should be EXACT matches to elements on this list. '
              'Please try to find more than one style if this is possible. '
              'If you really don\'t know, answer with ["Random Style"]'
              f'Here is the list: {all_fc_styles}')


def ask_an_llm(prompt: str):
    url = 'https://openrouter.ai/api/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'HTTP-Referer': f'{APP_TAG}',
        'X-Title': f'{APP_TAG}',
    }
    data = json.dumps({
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': SYS_PROMPT},
            {'role': 'user', 'content': prompt}
        ]})
    response = requests.post(
        url=url,
        headers=headers,
        data=data
    )

    return json.loads(response.text)


def prompt_to_style(prompt: str):
    resp = ask_an_llm(prompt)
    if resp is not None and 'choices' in resp and len(resp['choices']) > 0:
        choice = resp['choices'][0]
        if 'message' in choice and 'content' in choice['message']:
            return choice['message']['content']
    return "['Random Style']"  # default style

# resp1 = prompt_to_style('a pond like Monet')
# print(resp1)
