import json
from datetime import datetime

from flask import redirect, url_for, request, render_template, Blueprint
from flask_login import login_required, current_user

from banners.data.delete.deleting_repository import get_deleted_banners
from banners.data_old.banner_image_generator import get_image_data_url
from main.main import is_banner_admin

deleted_banners_blueprint = Blueprint('deleted_banners', __name__)

@deleted_banners_blueprint.route('/be/dashboard/deleted_banners')
@login_required
def deleted_banners_list():
    if not is_banner_admin(current_user.email):
        return redirect(url_for('main.profile'))

    page = request.args.get('page', 0, type=int)
    daily_banners_data = get_deleted_banners(page)

    banners_with_images = []
    for banner in daily_banners_data:
        banner_dict = {
            'banner_id': banner.id,
            'date': datetime.fromtimestamp(banner.date / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': get_image_data_url(json.loads(banner.layers)) if banner.layers else None
        }
        banners_with_images.append(banner_dict)

    return render_template('deleted_banners_list.html', daily_banners=banners_with_images, page=page)
