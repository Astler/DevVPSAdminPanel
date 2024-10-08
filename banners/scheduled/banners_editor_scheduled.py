from datetime import datetime
from sqlalchemy import func, desc
from banners.data.daily.daily_banner_item import DailyBannerItem
from cat.utils.telegram_utils import send_telegram_msg_to_me
from core.dependencies import app_sqlite_db


def get_least_used_banner():
    banner_count = app_sqlite_db.session.query(
        DailyBannerItem.banner_id,
        func.count(DailyBannerItem.banner_id).label('count')
    ).group_by(DailyBannerItem.banner_id).subquery()

    least_used_banner = app_sqlite_db.session.query(DailyBannerItem, banner_count.c.count) \
        .join(banner_count, DailyBannerItem.banner_id == banner_count.c.banner_id) \
        .order_by(banner_count.c.count, DailyBannerItem.date) \
        .first()

    return least_used_banner


def check_for_daily_banner():
    today = datetime.today()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_milli_seconds = int(today_start.timestamp() * 1000)

    banner = app_sqlite_db.session.query(DailyBannerItem).filter(DailyBannerItem.date == today_milli_seconds).first()

    if banner is not None:
        return

    send_telegram_msg_to_me("No daily banner today!")

    least_used_banner, use_count = get_least_used_banner()
    if least_used_banner:
        # Update the date of the least used banner
        least_used_banner.date = today_milli_seconds

        # Increment the use count
        least_used_banner.use_count = use_count + 1

        app_sqlite_db.session.commit()
        send_telegram_msg_to_me(
            f"Updated date for banner: {least_used_banner.banner_id}. New use count: {least_used_banner.use_count}")
    else:
        send_telegram_msg_to_me("No banners available to update!")