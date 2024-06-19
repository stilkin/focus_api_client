import copy
import json
import os.path

import requests

from fc_settings import all_fc_styles, default_cfg

SERVER_IP = '192.168.178.25'

PROMPT_CMD = '/focus '
CONFIG_CMD = '/focus_cfg '

CONFIG_LIST = 'LIST'
CONFIG_CLEAR = 'CLEAR'
CONFIG_ADD_STYLE = 'APPEND_STYLE'

TEMP_FOLDER = 'tmp/'
CFG_FOLDER = 'cfg/'


def handle_config_request(cfg_request, user_id=None):
    if user_id is None:
        return f'Sorry, I do not know who this user is.'

    if not os.path.exists(CFG_FOLDER):
        os.mkdir(CFG_FOLDER)

    config_file = f'{CFG_FOLDER}{user_id}.json'
    user_config = load_dict(config_file)
    if user_config is None:
        user_config = {}  # create empty config

    cfg_command = cfg_request.replace(CONFIG_CMD, '', 1)
    setting_name = cfg_command.split(' ', 1)[0]
    setting_value = cfg_command.replace(f'{setting_name} ', '', 1)

    print(f'Config request: "{setting_name}" with "{setting_value}"')

    if setting_name == CONFIG_LIST:
        return f'Current config:\n{json.dumps(user_config, indent=2)}'

    if setting_name == CONFIG_CLEAR:
        if setting_value in user_config:
            user_config.pop(setting_value)
            save_dict(config_file, user_config)
            return f'I have removed `{setting_value}` from your config.'
        else:
            return f'Setting {setting_value} not found in your config.'

    if setting_name == 'performance_selection':
        valid_settings = ['Quality', 'Speed', 'Extreme Speed']
        if setting_value not in valid_settings:
            return f'Setting `{setting_name}` with `{setting_value}` is not a valid config entry'

    if setting_name == 'style_selections':
        if setting_value not in all_fc_styles:
            return f'Setting `{setting_name}` with `{setting_value}` is not a valid config entry'
        else:
            setting_value = [setting_value]  # needs to be an array

    if setting_name == CONFIG_ADD_STYLE:
        if setting_value not in all_fc_styles:
            return f'Setting `{setting_name}` with `{setting_value}` is not a valid config entry'
        else:
            current_styles = user_config.get('style_selections')
            if setting_value not in current_styles:
                current_styles.append(setting_value)
            setting_name = 'style_selections'
            setting_value = current_styles

    user_config.update({setting_name: setting_value})
    save_dict(config_file, user_config)

    # default response
    return f'I have added `{setting_name}` with `{setting_value}` to your config.'


def image_from_prompt(prompt, user_id=None):
    try:
        json_response = generate_image(prompt, user_id)
        resp_obj = json.loads(json_response)

        if len(resp_obj) > 0:
            resp_obj = resp_obj[0]
            if 'url' in resp_obj:
                image_url = resp_obj['url'].replace('127.0.0.1', SERVER_IP)
                local_copy = download_file(image_url)
                return local_copy
    except Exception as ex:
        print(f'Something went wrong when trying to generate image: {ex.args}')
        return None


def generate_image(prompt, user_id=None):
    import requests
    import json

    url = f'http://{SERVER_IP}:7878/v1/generation/text-to-image'

    current_config = copy.deepcopy(default_cfg)
    current_config.update({'prompt': prompt})

    user_config = {}

    if user_id is not None:
        file_config = load_dict(f'{CFG_FOLDER}{user_id}.json')
        if file_config is not None:
            user_config = file_config

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

    if not os.path.exists(TEMP_FOLDER):
        os.mkdir(TEMP_FOLDER)

    if file_resp.status_code == 200:
        with open(file_local, 'wb') as file:
            file.write(file_resp.content)
        return file_local
    return None


def save_dict(file_name, dictionary):
    try:
        with open(file_name, "w") as json_file:
            json.dump(dictionary, json_file)
    except:
        print(f'Error opening file: {file_name}')


def load_dict(file_name):
    json_object = None
    try:
        with open(file_name, 'r') as json_file:
            json_object = json.load(json_file)
    except:
        print(f'Error opening file: {file_name}')

    return json_object
