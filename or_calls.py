import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('OPENROUTER_TOKEN')
APP_URI = 'https://stilkin.eu'
APP_TAG = 'Img Prompt Gen'
MODEL = 'openai/gpt-4o-mini'
SYS_PROMPT = (f'You are an assistant that has to work with prompt requests for image generation. '
              'You need to do two things with these prompts. '
              'Firstly, you have to "enrich" the prompt (make it more verbose, clear, explicit). '
              'Secondly, you have to determine which styles match best with this prompt.'
              'Answer only with a valid JSON object that contains two fields: "prompt" and "style".'
              'If you feel like you need to tell me something beyond that, '
              'you can add an extra field called "debug" and put your message there.')


def ask_an_llm(user_prompt: str, sys_prompt=SYS_PROMPT):
    url = 'https://openrouter.ai/api/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'HTTP-Referer': f'{APP_URI}',
        'X-Title': f'{APP_TAG}',
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': sys_prompt},
            {'role': 'user', 'content': user_prompt}
        ]})
    response = requests.post(
        url=url,
        headers=headers,
        data=data
    )

    return json.loads(response.text)


def expand_prompt(user_prompt: str):
    resp = ask_an_llm(user_prompt)
    if resp is not None and 'choices' in resp and len(resp['choices']) > 0:
        choice = resp['choices'][0]
        if 'message' in choice and 'content' in choice['message']:
            return json.loads(choice['message']['content'])
    return {'prompt': user_prompt, 'style': None}  # default


# resp1 = expand_prompt('a pond like Monet')
# print(resp1)
