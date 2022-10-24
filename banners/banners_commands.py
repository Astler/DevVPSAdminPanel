import os
import time
from datetime import datetime

import simplejson as json
from firebase_admin import firestore
from flask import Blueprint, request, Response
from flask_login import login_required
from werkzeug.exceptions import BadRequest

from application import db
from application.base_response import BaseResponse
from banners.data import check_file_by_path, get_last_update_time, set_last_update_time, \
    send_telegram_msg_to_me, banners_editor_saves, add_banners_editor_admin, get_formatted_be_saves_json
from banners.types.be_admin_data import BannersEditorAdminData
from config import BE_BANNERS_MAP, BE_MAP_UPDATE_HOURS

banners_api_blueprint = Blueprint('banners_api', __name__)

banners_folder = u'shared_banners'


class DailyBannerItem(db.Model):
    record_id = db.Column(db.Integer, primary_key=True)
    banner_id = db.Column(db.String(100), unique=True)
    date = db.Column(db.BigInteger)


class BannerServerItem:
    name = ""
    id = ""
    date = ""


def check_admins_banner_request(request_parameters: dict) -> BaseResponse:
    if not request_parameters.__contains__("admin"):
        return BaseResponse(False, "You need to provide your admin id to perform this action",
                            request_parameters)

    if not request_parameters.__contains__("id"):
        return BaseResponse(False, "Do you forgot to add banner id?", request_parameters)

    admin_id = request_parameters["admin"]
    be_server_settings = banners_editor_saves()

    if not be_server_settings.admins.__contains__(admin_id):
        return BaseResponse(False, f"User {admin_id} is not admin!", request_parameters)

    return BaseResponse(True, request_data=request_parameters)


@banners_api_blueprint.route('/be_admin_delete_banner', methods=['GET', 'POST'])
def delete_banner_by_admin() -> Response:
    content = request.args.to_dict()

    check_result = check_admins_banner_request(content)

    if not check_result.success:
        return check_result.to_response()

    admin_id = content["admin"]
    banner_id = content["id"]

    firestore_client = firestore.client()

    banner_ref = firestore_client.collection(banners_folder).document(banner_id)
    banner_data = banner_ref.get().to_dict()

    if banner_data is None:
        return BaseResponse(False, f"Banner with id {banner_id} not found!", content).to_response()

    send_telegram_msg_to_me(f"Admin with id {admin_id} requested deletion of this banner {banner_id}\n\n{banner_data}")

    try:
        firestore_client.collection(banners_folder).document(banner_id).delete()
    except Exception as error:
        return BaseResponse(False, str(error), content).to_response()

    return BaseResponse(True).to_response()


@banners_api_blueprint.route('/be_add_to_daily_queue', methods=['GET', 'POST'])
def add_to_daily_queue() -> Response:
    content = request.args.to_dict()

    check_result = check_admins_banner_request(content)

    if not check_result.success:
        return check_result.to_response()

    admin_id = content["admin"]
    banner_id = content["id"]

    banner_with_id = db.session.query(DailyBannerItem).filter(DailyBannerItem.banner_id == banner_id).first()

    if banner_with_id is not None:
        return BaseResponse(False, f"Banner with this ID {banner_id} already is queue!", content).to_response()

    last_banner = db.session.query(DailyBannerItem).order_by(DailyBannerItem.record_id.desc()).first()
    print(last_banner)

    today = datetime.today().strftime('%Y-%m-%d') + " 00:00:00"
    dt_obj = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
    milli_seconds = dt_obj.timestamp() * 1000

    if last_banner is None:
        date = milli_seconds
    else:
        date = last_banner.date + 86400000

    date_for_banner = time.strftime('%Y-%m-%d %H:%M:%S:{}'.format(date % 1000), time.gmtime(date / 1000.0))
    print(date_for_banner)

    new_banner = DailyBannerItem(banner_id=banner_id, date=date)

    db.session.add(new_banner)
    db.session.commit()

    send_telegram_msg_to_me(
        f"Admin with id {admin_id} added {banner_id} to daily queue. This banner date is {date_for_banner}")

    return BaseResponse(True).to_response()


@banners_api_blueprint.route('/be_map_version', methods=['GET'])
def get_map_version():
    return get_last_update_time()


@banners_api_blueprint.route('/be_settings', methods=['GET'])
def get_be_saves():
    return get_formatted_be_saves_json()


@banners_api_blueprint.route('/be_add_admin', methods=['GET', 'POST'])
@login_required
def be_add_admin():
    content = request.args.to_dict()

    admin_data = BannersEditorAdminData.from_json(json.loads(str(content).replace("\'", "\"")))

    if len(admin_data.id) == 0:
        raise BadRequest()

    return add_banners_editor_admin(admin_data)


@banners_api_blueprint.route('/be_map', methods=['GET'])
def get_banners():
    try:
        last_time = float(get_last_update_time())
    except Exception as error:
        print(error)
        last_time = 0

    if time.time() >= float(last_time) + float(BE_MAP_UPDATE_HOURS) * 60 * 60:
        if os.path.exists(BE_BANNERS_MAP):
            os.remove(BE_BANNERS_MAP)

        send_telegram_msg_to_me("Banners map create request!")

        set_last_update_time()
        data = update_server_banners_map()
    else:
        # send_telegram_msg_to_me("Loading?!")
        data = check_file_by_path(BE_BANNERS_MAP, "r").read()

    return data


@banners_api_blueprint.route('/be_check_empty_patterns', methods=['GET'])
def be_check_empty_patterns():
    return get_banners_without_pattern()


def update_server_banners_map() -> str:
    file = check_file_by_path(BE_BANNERS_MAP, "w")

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


def get_banners_without_pattern() -> str:
    db = firestore.client()

    send_telegram_msg_to_me("Готово! Получаю баннеры...")

    users_ref = db.collection(u'shared_banners')
    docs = users_ref.stream()

    items = []

    for doc in docs:
        resultdict = doc.to_dict()
        pattern = resultdict["moriginalLayersCode"]

        if pattern != None and len(pattern) != 0:
            items.append(resultdict["mid"])

    json_data = json.JSONEncoder(sort_keys=True, indent=4 * ' ', ensure_ascii=False).encode(items)

    send_telegram_msg_to_me(f"Найдено {len(items)} баннеров!")

    return json_data
