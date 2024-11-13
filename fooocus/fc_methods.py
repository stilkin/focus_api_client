import copy
import json
import os.path

from fc_settings import all_fc_styles, default_cfg
from tools.utilities import save_dict, load_dict, download_file

SERVER_IP = '192.168.178.25'

CONFIG_LIST = 'LIST'
CONFIG_CLEAR = 'CLEAR'
CONFIG_ADD_STYLE = 'APPEND_STYLE'

TEMP_FOLDER = 'tmp/'
CFG_FOLDER = 'cfg/'


def handle_config_request(cfg_command, user_id=None):
    if user_id is None:
        return f'Sorry, I do not know who this user is.'

    if not os.path.exists(CFG_FOLDER):
        os.mkdir(CFG_FOLDER)

    setting_name = cfg_command.split(' ', 1)[0]
    setting_value = cfg_command.replace(f'{setting_name} ', '', 1)
    print(f'Config request: "{setting_name}" with "{setting_value}"')

    config_file = f'{CFG_FOLDER}{user_id}.json'
    user_config = load_dict(config_file)
    if user_config is None:
        user_config = {}  # create empty config

    if setting_name == CONFIG_LIST:
        return f'Current config:\n{json.dumps(user_config, indent=2)}'

    if setting_name == CONFIG_CLEAR:
        if setting_value in user_config:
            user_config.pop(setting_value)
            save_dict(config_file, user_config)
            return f'I have removed `{setting_value}` from your config.'
        else:
            return f'Setting {setting_value} not found in your config.'

    if setting_name not in default_cfg:
        return f'I do not know a setting called "{setting_name}"...'

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


def image_from_prompt(prompt, user_id=None, custom_styles=None):
    print(f'Generating image with prompt: {prompt}')
    try:
        json_response = generate_image(prompt, user_id, custom_styles)
        resp_obj = json.loads(json_response)

        if len(resp_obj) > 0:
            resp_obj = resp_obj[0]
            if 'url' in resp_obj:
                image_url = resp_obj['url'].replace('127.0.0.1', SERVER_IP)
                local_copy = download_file(image_url, TEMP_FOLDER)
                return local_copy
    except Exception as ex:
        print(f'Something went wrong when trying to generate image: {ex.args}')
        return None


def generate_image(prompt, user_id=None, custom_styles=None):
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

    if custom_styles is not None:
        print(f'Setting style_selections to {custom_styles}')
        current_config.update({'style_selections': json.loads(custom_styles)})

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-API-KEY': 'Q2pLCMfmR597P6rtw4bDZXhAc'
    }
    payload = json.dumps(current_config)

    response = requests.request('POST', url, headers=headers, data=payload)
    return response.text
