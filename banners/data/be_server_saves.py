import json
import time
from datetime import datetime

import config
from application import db
from application.ios_utils import open_internal_file
from banners.db.daily_banner_item import DailyBannerItem
from banners.types.be_admin_data import BannersEditorAdminData
from banners.types.be_saves import BannersEditorSaves
from banners.types.be_settings import BannersEditorSettings

local_cached_saves: BannersEditorSaves = None


#
# App Settings
#

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

    saves = read_banners_saves()

    settings.admins = saves.admins
    settings.map_update_time = saves.map_update_time
    settings.daily_banner_id = banner_for_date.banner_id

    return str(settings.to_json()).replace("\'", "\"")


#
# Admins
#

def register_admin(admin_data: BannersEditorAdminData) -> str:
    write_banners_saves(read_banners_saves().try_add_admin(admin_data))
    return "Admin added!"


#
# Update time
#

def get_last_update_time() -> str:
    if local_cached_saves is not None:
        return local_cached_saves.map_update_time

    saves = read_banners_saves()
    return saves.map_update_time


def set_last_update_time():
    saves = read_banners_saves()
    saves.map_update_time = str(time.time())
    write_banners_saves(saves)


#
# Save/Read actually
#

def read_banners_saves() -> BannersEditorSaves:
    file = open_internal_file(config.BE_SERVER_SAVES, "r")

    contents = file.read()

    if len(contents) != 0:
        saves = BannersEditorSaves.from_json(json.loads(contents))
    else:
        saves = BannersEditorSaves()
        write_banners_saves(saves)

    global local_cached_saves

    if local_cached_saves is None:
        local_cached_saves = saves

    return saves


def write_banners_saves(saves: BannersEditorSaves):
    file = open_internal_file(config.BE_SERVER_SAVES, "w")
    file.write(json.dumps(saves.to_json()))
    file.close()

    global local_cached_saves

    if local_cached_saves is None:
        local_cached_saves = saves
