from datetime import datetime

from flask import redirect, url_for, request, render_template, Blueprint
from flask_login import login_required, current_user

from admin.data.flask_login import check_is_admin_or_exit
from admin.data.project_ids import ProjectId
from banners.data.daily.daily_banners_repository import get_daily_banners

from banners.data_old.banner_image_generator import get_image_data_url_by_id

daily_banners_blueprint = Blueprint('daily_banners', __name__)

@daily_banners_blueprint.route('/be/dashboard/daily_banners')
@login_required
def daily_banners_list():
    if not check_is_admin_or_exit(ProjectId.BANNERS_EDITOR):
        return

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
