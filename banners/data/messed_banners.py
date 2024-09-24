# todo create more complex validation for banners
import json
import time
from typing import Optional, Any

from banners.constants import banners_folder, incorrect_banners_data
from banners.data.banner_firebase_item import BannerFirebaseItem
from banners.data.messed_banners_info import MessedBannersInfo
from cat.utils.firebase_utils import get_mc_firestore_collection
from cat.utils.ios_utils import open_internal_file
from cat.utils.telegram_utils import send_telegram_msg_to_me


def messed_banners_info() -> MessedBannersInfo:
    file = open_internal_file(incorrect_banners_data, "r")
    data = file.read()
    file.close()

    if len(data) <= 0:
        return None

    messed_info = MessedBannersInfo.from_json(json.loads(data))
    return messed_info


def find_messed_banners() -> str:
    docs = get_mc_firestore_collection(banners_folder).stream()

    items = []

    for doc in docs:
        banner = BannerFirebaseItem.from_dict(doc.to_dict())
        if len(banner.unique_banner_code) <= 0:
            items.append(banner.mid)

    messed_info = MessedBannersInfo(items, time.time())
    json_data = messed_info.to_json()

    send_telegram_msg_to_me(f"Found {len(items)} messed banners!\n\n{json_data}")

    with open_internal_file(incorrect_banners_data, "w") as file:
        file.write(json_data)

    return json_data
