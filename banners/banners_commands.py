import firebase_admin
import simplejson as json
from firebase_admin import credentials, firestore
from flask import Blueprint

from banners.data import get_cer_data
from config import PROJECT_ID, BANNERS_MAP_FILE

banners_api = Blueprint('banners_api', __name__)


class BannerServerItem:
    name = ""
    id = ""
    date = ""


@banners_api.route('/get_all_banners', methods=['GET'])
def get_banners():
    update_server_banners_map()
    return """All banners!"""


def update_server_banners_map():
    # msg = await bot.send_message(message.chat.id, "Подключаюсь к Firebase...")
    cred = credentials.Certificate(get_cer_data())

    firebase_admin.initialize_app(cred, {
        'projectId': PROJECT_ID,
    })

    db = firestore.client()

    # await msg.edit_text("Готово! Получаю баннеры...")

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

    f = open(BANNERS_MAP_FILE, "w", encoding='utf-8')
    f.write(json_data)
    f.close()

    # await msg.edit_text(f"Для загрузки найдено {len(items)} баннеров!", reply_markup=publish_keyboard())

    # async with state.proxy() as data:
    #     data['request_id'] = msg.message_id

    f = open(BANNERS_MAP_FILE, "w", encoding='utf-8')
    f.write(json_data)
    f.close()

    # await DataBannersState.actionUserWait.set()
