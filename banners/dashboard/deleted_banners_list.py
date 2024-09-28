from flask import request, render_template, Blueprint
from flask_login import login_required
from typing import List, Dict

from admin.data.flask_login import check_is_admin_or_exit
from admin.data.project_ids import ProjectId
from banners.data.delete.deleting_repository import get_deleted_banners
from banners.types.deleted_banner import DeletedBannerModel

deleted_banners_blueprint = Blueprint('deleted_banners', __name__)

def get_page_number() -> int:
    return request.args.get('page', 0, type=int)

def fetch_deleted_banners(page: int) -> List[DeletedBannerModel]:
    return get_deleted_banners(page)

def prepare_banners_for_ui(banners: List[DeletedBannerModel]) -> List[Dict]:
    return [banner.to_ui_info() for banner in banners]

@deleted_banners_blueprint.route('/be/dashboard/deleted_banners')
@login_required
def deleted_banners_list():
    if not check_is_admin_or_exit(ProjectId.BANNERS_EDITOR):
        return

    page = get_page_number()
    deleted_banners_data = fetch_deleted_banners(page)
    banners_with_images = prepare_banners_for_ui(deleted_banners_data)

    return render_template('deleted_banners_list.html',
                           daily_banners=banners_with_images,
                           page=page)