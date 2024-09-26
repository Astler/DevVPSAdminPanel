from datetime import datetime

from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_login import login_required, current_user

from banners.banners_commands import get_daily_banner
from banners.data.admin_actions import get_all_admin_actions, count_admins
from banners.data.banner_image_generator import get_image_data_url_by_id
from banners.data.banners_mapping import get_last_mapping_update, count_mapped_banners
from banners.data.daily_banners import get_daily_banners
from banners.data.messed_banners import messed_banners_info
from main.main import is_banner_admin

dashboard_blueprint = Blueprint('dashboard_blueprint', __name__)


@dashboard_blueprint.route('/be_dashboard')
@login_required
def banners_dashboard():
    if not is_banner_admin(current_user.email):
        return redirect(url_for('main.profile'))

    daily_banner_data = get_daily_banner()

    if not daily_banner_data:
        return render_template('banners_dashboard.html', banner_data=None)

    messed = messed_banners_info()

    return render_template(
        'banners_dashboard.html',
        sign_up_enabled=current_app.config['SIGN_UP_ENABLED'],
        daily_banner_url=get_image_data_url_by_id(daily_banner_data.daily_banner_id),
        daily_banner_id=daily_banner_data.daily_banner_id,
        messed_banners=len(messed.banners) if messed is not None else "No messed banners data found!",
        messed_banners_update_time=messed.formatted_time() if messed is not None else "-- -- --",
        last_mapping_time=get_last_mapping_update(),
        total_banners=count_mapped_banners(),
        admin_logs=get_all_admin_actions(),
        admins_count=count_admins()
    )


@dashboard_blueprint.route('/be_dashboard/daily_banners')
@login_required
def daily_banners_list():
    if not is_banner_admin(current_user.email):
        return redirect(url_for('main.profile'))

    page = request.args.get('page', 0, type=int)
    daily_banners_data = get_daily_banners(page)

    banners_with_images = []
    for banner in daily_banners_data:
        banner_dict = {
            'banner_id': banner.banner_id,
            'date': datetime.fromtimestamp(banner.date / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': get_image_data_url_by_id(banner.banner_id)
        }
        banners_with_images.append(banner_dict)

    return render_template('daily_banners_list.html', daily_banners=banners_with_images, page=page)