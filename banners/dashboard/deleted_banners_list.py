from flask import request, render_template, Blueprint
from flask_login import login_required

from admin.data.flask_login import check_is_admin_or_exit
from admin.data.project_ids import ProjectId
from banners.data.delete.deleting_repository import paginate_deleted_banners

deleted_banners_blueprint = Blueprint('deleted_banners', __name__)

@deleted_banners_blueprint.route('/be/dashboard/deleted_banners')
@login_required
def deleted_banners_list():
    if not check_is_admin_or_exit(ProjectId.BANNERS_EDITOR):
        return

    page = request.args.get('page', 1, type=int)
    raw_banners = paginate_deleted_banners(page)
    return render_template('deleted_banners_list.html',
                           pagination=raw_banners,
                           page=page)