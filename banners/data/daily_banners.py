import json
from datetime import datetime, timedelta

from sqlalchemy import func

from application import app_sqlite_db
from banners.db.daily_banner_item import DailyBannerItem, DailyBannerItemEncoder
from banners.types.dialy_banner import DailyBanner
from config import BE_PAGE_SIZE


def get_daily_banners(request=None) -> str:
    request_parameters = request.args.to_dict()

    if not request_parameters.__contains__("page"):
        page = 0
    else:
        page = int(request_parameters["page"])

    today = datetime.today().strftime('%Y-%m-%d') + " 00:00:00"
    dt_obj = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
    today_milli_seconds = dt_obj.timestamp() * 1000

    banners = app_sqlite_db.session.query(DailyBannerItem).filter(DailyBannerItem.date < today_milli_seconds).order_by(
        DailyBannerItem.date.desc())

    selection = []

    last_item_index = (page + 1) * BE_PAGE_SIZE
    first_item_index = page * BE_PAGE_SIZE

    if banners.count() < last_item_index:
        last_item_index = banners.count()

    for banner in banners[first_item_index:last_item_index]:
        selection.append(banner)

    return str(json.dumps(selection, ensure_ascii=False, cls=DailyBannerItemEncoder)).replace("\'", "\"")


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
