import json
from datetime import datetime, timedelta

from flask import Response
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import func

from core.dependencies import app_sqlite_db
from application.base_response import BaseResponse
from banners.data.actions.action_item import AdminActionModel, AdminAction
from banners.data.admin_repository import admin_validation
from banners.data.daily.daily_banner_item import DailyBannerItem, DailyBannerItemEncoder
from banners.data.daily.dialy_banner import DailyBanner
from banners.data.firebase.firestore_repository import get_be_shared
from banners.data_old.banner_image_generator import get_layers_from_web
from cat.utils.telegram_utils import send_telegram_msg_to_me
from config import BE_PAGE_SIZE


def paginate_daily_banners(page=1) -> Pagination:
    pagination = app_sqlite_db.session.query(DailyBannerItem).order_by(DailyBannerItem.date.desc()).paginate(
        page=page, per_page=BE_PAGE_SIZE, error_out=False
    )

    for banner in pagination.items:
        if banner.layers is None:
            banner.layers = json.dumps(get_layers_from_web(banner.banner_id), ensure_ascii=False,
                              cls=DailyBannerItemEncoder)
            app_sqlite_db.session.add(banner)

    app_sqlite_db.session.commit()

    pagination.items = [banner.to_ui_info() for banner in pagination.items]

    return pagination


def generate_daily_banners_response(request=None) -> str:
    request_parameters = request.args.to_dict()

    if not request_parameters.__contains__("page"):
        page = 0
    else:
        page = int(request_parameters["page"])

    banners = paginate_daily_banners(page).items

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
        return BaseResponse(False, f"Banner with this ID {banner_id} is already in queue!", content).to_response()

    banner_data = get_be_shared().document(banner_id).get().to_dict()
    if banner_data is None:
        return BaseResponse(False, f"Banner with id {banner_id} not found!", content).to_response()

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    today_timestamp = int(today.timestamp() * 1000)

    next_available_date = today_timestamp
    while True:
        existing_banner = app_sqlite_db.session.query(DailyBannerItem).filter(
            DailyBannerItem.date == next_available_date).first()
        if existing_banner is None:
            break
        next_available_date += 86400000  # Add one day in milliseconds

    new_banner = DailyBannerItem(banner_id=banner_id, date=next_available_date)
    app_sqlite_db.session.add(new_banner)

    app_sqlite_db.session.add(AdminActionModel.build(
        admin_id=admin_id,
        action_info=banner_data,
        action=AdminAction.AddedDaily
    ))

    app_sqlite_db.session.commit()

    date_for_banner = datetime.fromtimestamp(next_available_date / 1000.0).strftime('%Y-%m-%d %H:%M:%S')

    send_telegram_msg_to_me(
        f"Admin with id {admin_id} added {banner_id} to daily queue. This banner date is {date_for_banner}")

    return BaseResponse(True).to_response()


def get_daily_banner(request_parameters=None) -> DailyBanner | None:
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
