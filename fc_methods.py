import copy
import json
import os.path

import requests

from fc_settings import all_fc_styles, default_cfg

SERVER_IP = '192.168.178.25'

PROMPT_CMD = '/focus '
CONFIG_CMD = '/focus_cfg '

TEMP_FOLDER = 'tmp/'
CFG_FOLDER = 'cfg/'

user_config = {
    'performance_selection': "Extreme Speed",
}


async def handle_config_request(cfg_request):
    cfg_command = cfg_request.replace(CONFIG_CMD, '', 1)
    setting_name = cfg_command.split(' ', 1)[0]
    setting_value = cfg_command.replace(f'{setting_name} ', '', 1)

    print(f'Attempting to set "{setting_name}" to "{setting_value}"')

    if setting_name == 'performance_selection':
        valid_settings = ['Quality', 'Speed', 'Extreme Speed']
        if setting_value in valid_settings:
            user_config.update({setting_name: setting_value})
            return f'Updated setting `{setting_name}` successfully'

    if setting_name == 'style_selections':
        if setting_value in all_fc_styles:
            user_config.update({setting_name: [setting_value]})
            return f'Updated setting `{setting_name}` successfully'

    # default response
    return f'Setting `{setting_name}` with `{setting_value}` is not a valid config entry'


def image_from_prompt(prompt):
    try:
        json_response = generate_image(prompt)
        resp_obj = json.loads(json_response)

        if len(resp_obj) > 0:
            resp_obj = resp_obj[0]
            if 'url' in resp_obj:
                image_url = resp_obj['url'].replace('127.0.0.1', SERVER_IP)
                local_copy = download_file(image_url)
                return local_copy
    except:
        print('Something went wrong when trying to generate image...')
        return None


def generate_image(prompt):
    import requests
    import json

    url = f'http://{SERVER_IP}:7878/v1/generation/text-to-image'

    current_config = copy.deepcopy(default_cfg)
    current_config.update({'prompt': prompt})

    for param in user_config:
        if param in current_config:
            print(f'Setting {param} to {user_config.get(param)}')
            current_config.update({param: user_config.get(param)})

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-API-KEY': 'Q2pLCMfmR597P6rtw4bDZXhAc'
    }
    payload = json.dumps(current_config)

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


def download_file(file_url):
    file_resp = requests.get(file_url)
    file_local = file_url.rsplit('/', 1)[-1]
    file_local = f'tmp/{file_local}'
    if file_resp.status_code == 200:
        with open(file_local, 'wb') as file:
            file.write(file_resp.content)
        return file_local
    return None


# main code block

if not os.path.exists(TEMP_FOLDER):
    print(f'Folder f{TEMP_FOLDER} does not exist, creating...')
    os.mkdir(TEMP_FOLDER)
