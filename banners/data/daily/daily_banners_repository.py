import json
import time
from datetime import datetime, timedelta

from flask import Response
from sqlalchemy import func

from application import app_sqlite_db
from application.base_response import BaseResponse
from banners.data.actions.action_item import ActionItem, AdminAction
from banners.data.admin_repository import admin_validation
from banners.data.daily.daily_banner_item import DailyBannerItem, DailyBannerItemEncoder
from banners.data.daily.dialy_banner import DailyBanner
from banners.data.firebase.firestore_repository import get_be_shared
from cat.utils.telegram_utils import send_telegram_msg_to_me
from config import BE_PAGE_SIZE


def get_daily_banners(page=0) -> []:
    banners = app_sqlite_db.session.query(DailyBannerItem).order_by(DailyBannerItem.date.desc())

    selection = []

    last_item_index = (page + 1) * BE_PAGE_SIZE
    first_item_index = page * BE_PAGE_SIZE

    if banners.count() < last_item_index:
        last_item_index = banners.count()

    for banner in banners[first_item_index:last_item_index]:
        selection.append(banner)

    return selection


def generate_daily_banners_response(request=None) -> str:
    request_parameters = request.args.to_dict()

    if not request_parameters.__contains__("page"):
        page = 0
    else:
        page = int(request_parameters["page"])

    banners = get_daily_banners(page)

    return str(json.dumps(banners, ensure_ascii=False, cls=DailyBannerItemEncoder)).replace("\'", "\"")


def add_to_daily(request) -> Response:
    content = request.args.to_dict()

    check_result = admin_validation(content)

    if not check_result.success:
        return check_result.to_response()

    admin_id = content["admin"]
    banner_id = content["id"]

    check_for_duplicate = app_sqlite_db.session.query(DailyBannerItem).filter(
        DailyBannerItem.banner_id == banner_id).first()

    if check_for_duplicate is not None:
        return BaseResponse(False, f"Banner with this ID {banner_id} already is queue!", content).to_response()

    banner_data = get_be_shared().document(banner_id).get().to_dict()

    if banner_data is None:
        return BaseResponse(False, f"Banner with id {banner_id} not found!", content).to_response()

    last_day_banner = app_sqlite_db.session.query(DailyBannerItem).order_by(DailyBannerItem.record_id.desc()).first()

    today = datetime.today().strftime('%Y-%m-%d') + " 00:00:00"
    dt_obj = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
    milli_seconds = dt_obj.timestamp() * 1000

    if last_day_banner is None:
        date = milli_seconds
    else:
        date = last_day_banner.date + 86400000

    date_for_banner = time.strftime('%Y-%m-%d %H:%M:%S:{}'.format(date % 1000), time.gmtime(date / 1000.0))
    new_banner = DailyBannerItem(banner_id=banner_id, date=date)
    app_sqlite_db.session.add(new_banner)

    app_sqlite_db.session.add(
        ActionItem(admin_id=admin_id, action_info=json.dumps(banner_data), action=int(AdminAction.AddedDaily),
                   date=time.time()))

    app_sqlite_db.session.commit()

    send_telegram_msg_to_me(
        f"Admin with id {admin_id} added {banner_id} to daily queue. This banner date is {date_for_banner}")

    return BaseResponse(True).to_response()


def get_daily_banner(request_parameters=None) -> DailyBanner:
    if request_parameters is None:
        request_parameters = {}
    if not request_parameters.__contains__("date"):
        today = datetime.today()
    else:
        today = datetime.strptime(request_parameters["date"], '%Y-%m-%d')

    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_milli_seconds = int(today_start.timestamp() * 1000)

    banner = app_sqlite_db.session.query(DailyBannerItem).filter(DailyBannerItem.date == today_milli_seconds).first()

    if banner is None:
        seven_days_ago = today - timedelta(days=7)
        seven_days_ago_milli_seconds = int(seven_days_ago.timestamp() * 1000)

        banner = app_sqlite_db.session.query(DailyBannerItem) \
            .filter(DailyBannerItem.date < today_milli_seconds) \
            .filter(DailyBannerItem.date < seven_days_ago_milli_seconds) \
            .order_by(func.random()) \
            .first()

        if banner is None:
            return None
        else:
            banner.last_shown_date = today_milli_seconds
            app_sqlite_db.session.delete(banner)
            app_sqlite_db.session.commit()
            new_banner = DailyBannerItem(banner_id=banner.banner_id, date=today_milli_seconds)
            app_sqlite_db.session.add(new_banner)
            app_sqlite_db.session.commit()

    response = DailyBanner()
    response.daily_banner_id = banner.banner_id

    return response
