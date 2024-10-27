import json
import os
import time
from datetime import datetime

from banners.data.firebase.firestore_repository import get_be_shared
from banners.data.firebase.banner_firebase_item import BannerFirebaseItem
from banners.data.mapping.banner_server_item import BannerServerItem
from banners.data_old.be_server_saves import read_banners_saves, write_banners_saves
from cat.utils.ftp_utils import upload_file_to_folder
from cat.utils.ios_utils import open_internal_file
from cat.utils.telegram_utils import send_telegram_msg_to_me
from config import BE_BANNERS_MAP, BE_MAP_UPDATE_HOURS


def get_last_mapping_update() -> int:
    saves = read_banners_saves()
    return saves.last_mapping_time


def save_mapping_time():
    saves = read_banners_saves()
    saves.last_mapping_time = int(datetime.now().timestamp())
    write_banners_saves(saves)


def count_mapped_banners() -> int:
    banners_map = get_mapping()
    return len(json.loads(banners_map))


def get_mapping() -> str:
    try:
        last_time = float(get_last_mapping_update())
    except Exception as error:
        print(error)
        last_time = 0

    map_exists = os.path.exists(BE_BANNERS_MAP)

    if time.time() >= float(last_time) + float(BE_MAP_UPDATE_HOURS) * 60 * 60 or not map_exists:
        if map_exists:
            os.remove(BE_BANNERS_MAP)

        send_telegram_msg_to_me("Banners map create request!")

        save_mapping_time()
        data = generate_and_upload_banners_map()
    else:
        data = open_internal_file(BE_BANNERS_MAP, "r").read()

    return data.replace("\'", "_")


def generate_and_upload_banners_map() -> str:
    docs = get_be_shared().stream()

    items = []

    for doc in docs:
        banner = BannerFirebaseItem.from_dict(doc.to_dict())
        items.append(BannerServerItem(banner.banner_name, banner.mid, str(banner.mdate)))

    json_data = json.dumps([item.to_dict() for item in items], sort_keys=True, indent=4, ensure_ascii=False)

    with open_internal_file(BE_BANNERS_MAP, "w") as file:
        file.write(json_data)

    send_telegram_msg_to_me(f"Mapped {len(items)} banners!")

    try:
        upload_file_to_folder(BE_BANNERS_MAP)
    except Exception as e:
        print(e)

    return json_data
