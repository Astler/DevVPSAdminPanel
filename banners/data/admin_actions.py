import json
import time
from datetime import datetime

from flask import Response

from application import app_sqlite_db
from application.base_response import BaseResponse
from banners.constants import incorrect_banners_data, banners_folder
from banners.data.banner_firebase_item import BannerFirebaseItem
from banners.data.banner_image_generator import get_image_data_url
from banners.data.be_server_saves import read_banners_saves
from banners.db.admin_action_item import AdminActionItem, AdminAction
from banners.db.daily_banner_item import DailyBannerItem
from cat.utils.firebase_utils import get_firestore_collection
from cat.utils.telegram_utils import send_telegram_msg_to_me


def count_admins() -> int:
    saves = read_banners_saves()
    return len(saves.admins)


def get_all_admin_actions() -> []:
    actions = app_sqlite_db.session.query(AdminActionItem).order_by(AdminActionItem.record_id.desc()).all()

    result = []

    for action in actions:
        banner = BannerFirebaseItem.from_json(action.action_info)

        if banner is not None:
            action.banner_url = get_image_data_url(banner.layers, 1)

        action.translated_action = str(AdminAction.get_action_by_value(action.action).name)

        result.append(action)

    return result


def __check_admins_request(request_parameters: dict) -> BaseResponse:
    if not request_parameters.__contains__("admin"):
        return BaseResponse(False, "You need to provide your admin id to perform this action",
                            request_parameters)

    if not request_parameters.__contains__("id"):
        return BaseResponse(False, "Do you forgot to add banner id?", request_parameters)

    saves = read_banners_saves()

    admin_id = request_parameters["admin"]

    if not saves.admins.__contains__(admin_id):
        return BaseResponse(False, f"User {admin_id} is not admin!", request_parameters)

    return BaseResponse(True, request_data=request_parameters)


def add_to_daily(request) -> Response:
    content = request.args.to_dict()

    check_result = __check_admins_request(content)

    if not check_result.success:
        return check_result.to_response()

    admin_id = content["admin"]
    banner_id = content["id"]

    banner_with_id = app_sqlite_db.session.query(DailyBannerItem).filter(DailyBannerItem.banner_id == banner_id).first()

    if banner_with_id is not None:
        return BaseResponse(False, f"Banner with this ID {banner_id} already is queue!", content).to_response()

    banner_ref = get_firestore_collection(banners_folder).document(banner_id)
    banner_data = banner_ref.get().to_dict()

    if banner_data is None:
        return BaseResponse(False, f"Banner with id {banner_id} not found!", content).to_response()

    last_banner = app_sqlite_db.session.query(DailyBannerItem).order_by(DailyBannerItem.record_id.desc()).first()
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

    app_sqlite_db.session.add(new_banner)

    banner_ref = get_firestore_collection(banners_folder).document(banner_id)
    banner_data = banner_ref.get().to_dict()

    app_sqlite_db.session.add(
        AdminActionItem(admin_id=admin_id, action_info=json.dumps(banner_data), action=int(AdminAction.AddedDaily),
                        date=time.time()))

    app_sqlite_db.session.commit()

    send_telegram_msg_to_me(
        f"Admin with id {admin_id} added {banner_id} to daily queue. This banner date is {date_for_banner}")

    return BaseResponse(True).to_response()


def delete_banner(request) -> Response:
    content = request.args.to_dict()

    check_result = __check_admins_request(content)

    if not check_result.success:
        return check_result.to_response()

    admin_id = content["admin"]
    banner_id = content["id"]

    banner_ref = get_firestore_collection(banners_folder).document(banner_id)
    banner_data = banner_ref.get().to_dict()

    if banner_data is None:
        return BaseResponse(False, f"Banner with id {banner_id} not found!", content).to_response()

    send_telegram_msg_to_me(f"Admin with id {admin_id} requested deletion of this banner {banner_id}\n\n{banner_data}")

    app_sqlite_db.session.add(
        AdminActionItem(admin_id=admin_id, action_info=json.dumps(banner_data), action=int(AdminAction.Deleted),
                        date=time.time()))
    app_sqlite_db.session.commit()

    try:
        banner_ref.delete()
    except Exception as error:
        return BaseResponse(False, str(error), content).to_response()

    return BaseResponse(True).to_response()
