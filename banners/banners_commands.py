import time

import firebase_admin
import simplejson as json
from firebase_admin import credentials, firestore
from flask import Blueprint
import os

from banners.data import get_cer_data, check_file_by_path, get_last_update_time, set_last_update_time, \
    send_telegram_msg_to_me
from config import PROJECT_ID, BE_BANNERS_MAP, BE_MAP_UPDATE_HOURS

banners_api = Blueprint('banners_api', __name__)


class BannerServerItem:
    name = ""
    id = ""
    date = ""


@banners_api.route('/get_all_banners', methods=['GET'])
def get_banners():
    if time.time() >= get_last_update_time() + float(BE_MAP_UPDATE_HOURS) * 60 * 60:
        if os.path.exists(BE_BANNERS_MAP):
            os.remove(BE_BANNERS_MAP)

        send_telegram_msg_to_me("Banners map create request!")

        set_last_update_time()
        data = update_server_banners_map()
    else:
        send_telegram_msg_to_me("Loading?!")
        data = check_file_by_path(BE_BANNERS_MAP, "r").read()

    return data


def update_server_banners_map() -> str:
    file = check_file_by_path(BE_BANNERS_MAP, "w")

    send_telegram_msg_to_me("Подключаюсь к Firebase...")

    cred = credentials.Certificate(get_cer_data())

    firebase_admin.initialize_app(cred, {
        'projectId': PROJECT_ID,
    })

    db = firestore.client()

    send_telegram_msg_to_me("Готово! Получаю баннеры...")

    users_ref = db.collection(u'shared_banners')
    docs = users_ref.stream()

    items = []

    for doc in docs:
        resultdict = doc.to_dict()
        innerItem = BannerServerItem()
        innerItem.name = resultdict["mbannerName"]
        innerItem.id = resultdict["mid"]
        innerItem.date = resultdict["mdate"]
        items.append(innerItem)

    def encode_complex(obj):
        if isinstance(obj, BannerServerItem):
            return {
                "id": obj.id, "name": obj.name, "date": obj.date
            }
        raise TypeError(repr(obj) + " is not JSON serializable")

    json_data = json.JSONEncoder(default=encode_complex, sort_keys=True, indent=4 * ' ', ensure_ascii=False) \
        .encode(items)

    file.write(json_data)
    file.close()

    send_telegram_msg_to_me(f"Найдено {len(items)} баннеров!")

    return json_data
