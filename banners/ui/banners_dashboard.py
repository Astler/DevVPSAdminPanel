from flask import Blueprint, render_template
from flask_login import login_required

from application import sign_up_enabled
from banners.banners_commands import get_daily_banner
from banners.data.admin_actions import get_all_admin_actions, count_admins
from banners.data.banner_image_generator import get_image_data_url_by_id
from banners.data.banners_mapping import get_last_mapping_update, count_mapped_banners
from banners.data.messed_banners import messed_banners_info

dashboard_blueprint = Blueprint('dashboard_blueprint', __name__)


@dashboard_blueprint.route('/be/dashboard')
@login_required
def banners_dashboard():
    daily_banner_data = get_daily_banner()

    if not daily_banner_data:
        return render_template('banners_dashboard.html', banner_data=None)

    messed = messed_banners_info()

    return render_template(
        'banners_dashboard.html',
        sign_up_enabled=sign_up_enabled,
        daily_banner_url=get_image_data_url_by_id(daily_banner_data.daily_banner_id),
        daily_banner_id=daily_banner_data.daily_banner_id,
        messed_banners=len(messed.banners) if messed is not None else "No messed banners data found!",
        messed_banners_update_time=messed.formatted_time() if messed is not None else "-- -- --",
        last_mapping_time=get_last_mapping_update(),
        total_banners=count_mapped_banners(),
        admin_logs=get_all_admin_actions(),
        admins_count=count_admins()
    )
