import json
import os

import requests


def save_dict(file_name, dictionary):
    try:
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(dictionary, json_file)
    except:
        print(f'Error opening file: {file_name}')


def load_dict(file_name):
    json_object = None
    try:
        with open(file_name, 'r', encoding='utf-8') as json_file:
            json_object = json.load(json_file)
    except:
        print(f'Error opening file: {file_name}')

    return json_object


def download_file(file_url, local_folder):
    if not os.path.exists(local_folder):
        os.mkdir(local_folder)

    file_resp = requests.get(file_url)
    file_local = file_url.rsplit('/', 1)[-1]
    file_local = f'{local_folder}{file_local}'

    if file_resp.status_code == 200:
        with open(file_local, 'wb') as file:
            file.write(file_resp.content)
        return file_local
    return None
