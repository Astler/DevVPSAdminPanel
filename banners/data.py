import json
import os
import time

from github import GithubException

import config
from banners.be_saves import BannersEditorSaves
from config import CERT_PATH, A_PATH, BOT_TOKEN, MY_PROFILE_ID
from loader import repository

import requests


def send_telegram_msg_to_me(text: str):
    token = BOT_TOKEN
    chat_id = MY_PROFILE_ID
    url_req = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
    results = requests.get(url_req)
    print(results.json())


def check_file_by_path(path_to_file: str, open_mode: str = "a+"):
    if path_to_file.__contains__("/"):
        path = "".join(path_to_file.split("/")[:-1])
        os.makedirs(path, exist_ok=True)

    if not os.path.exists(path_to_file):
        return open(path_to_file, "a+")

    return open(path_to_file, open_mode)


def banners_editor_saves() -> BannersEditorSaves:
    file = check_file_by_path(config.BE_SERVER_SAVES, "r")

    contents = file.read()

    if len(contents) != 0:
        saves = BannersEditorSaves.from_json(json.loads(contents))
    else:
        saves = BannersEditorSaves()
        update_banners_editor_saves(saves)

    return saves


def update_banners_editor_saves(saves: BannersEditorSaves):
    file = check_file_by_path(config.BE_SERVER_SAVES, "w")
    file.write(json.dumps(saves.to_json()))
    file.close()


def get_last_update_time() -> int:
    saves = banners_editor_saves()
    return saves.last_banners_map_update_time


def set_last_update_time():
    saves = banners_editor_saves()
    saves.last_banners_map_update_time = time.time()
    update_banners_editor_saves(saves)


def get_cer_data():
    try:
        file = repository.get_contents(CERT_PATH)
        contents = file.decoded_content.decode()
        cer = json.loads(contents)
    except GithubException:
        cer = {}

    return cer


def get_a_list():
    try:
        file = repository.get_contents(A_PATH)
        contents = file.decoded_content.decode()
        a = json.loads(contents)
    except GithubException:
        a = []

    return a
