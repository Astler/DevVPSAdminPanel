import json
import os
import time
from datetime import datetime

from github import GithubException

import config
from application import db
from banners.banners_commands import DailyBannerItem
from banners.types.be_admin_data import BannersEditorAdminData
from banners.types.be_saves import BannersEditorSaves
from banners.types.be_settings import BannersEditorSettings
from config import CERT_PATH, A_PATH, BOT_TOKEN, MY_PROFILE_ID
from loader import repository

import requests


def get_banners_settings() -> str:
    today = datetime.today().strftime('%Y-%m-%d') + " 00:00:00"
    dt_obj = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
    today_in_millis = dt_obj.timestamp() * 1000

    requested_date = time.strftime('%Y-%m-%d %H:%M:%S:{}'.format(today_in_millis % 1000),
                                   time.gmtime(today_in_millis / 1000.0))
    print(requested_date)

    banner_for_date = db.session.query(DailyBannerItem).filter(DailyBannerItem.date == today_in_millis).first()

    if banner_for_date is None:
        banner_for_date = DailyBannerItem()
        print(f"there is no banner for {requested_date}")

    settings = BannersEditorSettings()

    saves = banners_editor_saves()

    settings.admins = saves.admins
    settings.map_update_time = saves.map_update_time
    settings.daily_banner_id = banner_for_date.banner_id

    return str(settings.to_json()).replace("\'", "\"")


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


def add_banners_editor_admin(admin_data: BannersEditorAdminData) -> str:
    saves = banners_editor_saves()

    admins = saves.admins

    if admins.__contains__(admin_data.id):
        return "Already admin!"

    admins.append(admin_data.id)

    update_banners_editor_saves(saves)

    return "Admin added!"


def get_last_update_time() -> str:
    saves = banners_editor_saves()
    return saves.map_update_time


def set_last_update_time():
    saves = banners_editor_saves()
    saves.map_update_time = str(time.time())
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
