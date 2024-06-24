import json
import os

import requests
from dotenv import load_dotenv

from fc_settings import all_fc_styles

load_dotenv()
TOKEN = os.getenv('OPENROUTER_TOKEN')
APP_TAG = 'focus-client.be'
MODEL = 'anthropic/claude-3.5-sonnet'
SYS_PROMPT = (f'You are an assistant that has to work with prompt requests for image generation. '
              'You need to do two things with these prompts. '
              'Firstly, you have to "enrich" the prompt (make it more verbose, clear, explicit). '
              'Secondly, you have to determine which styles match best with this prompt.'
              'Answer only with a valid JSON object that contains two fields: "prompt" and "style".'
              'If you feel like you need to tell me something beyond that, '
              'you can add an extra field called "debug" and put your message there.')


def ask_an_llm(prompt: str, sys_prompt=SYS_PROMPT):
    url = 'https://openrouter.ai/api/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'HTTP-Referer': f'{APP_TAG}',
        'X-Title': f'{APP_TAG}',
    }
    data = json.dumps({
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': sys_prompt},
            {'role': 'user', 'content': prompt}
        ]})
    response = requests.post(
        url=url,
        headers=headers,
        data=data
    )

    return json.loads(response.text)


def expand_prompt(prompt: str):
    resp = ask_an_llm(prompt)
    if resp is not None and 'choices' in resp and len(resp['choices']) > 0:
        choice = resp['choices'][0]
        if 'message' in choice and 'content' in choice['message']:
            return choice['message']['content']
    return '["Random Style"]'  # default style


# resp1 = expand_prompt('a pond like Monet')
# print(resp1)
