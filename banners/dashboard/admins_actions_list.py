from flask import request, render_template, Blueprint
from flask_login import login_required

from admin.data.flask_login import check_is_admin_or_exit
from admin.data.project_ids import ProjectId
from banners.data.actions.actions_repository import paginate_actions
from banners.data.daily.daily_banners_repository import paginate_daily_banners

admins_blueprint = Blueprint('admins_banners', __name__)

@admins_blueprint.route('/be/dashboard/admins_actions')
@login_required
def admins_actions_list():
    if not check_is_admin_or_exit(ProjectId.BANNERS_EDITOR):
        return

    page = request.args.get('page', 1, type=int)
    return render_template('admins_actions_list.html',
                           pagination=paginate_actions(page),
                           page=page)