from flask import request, render_template, Blueprint
from flask_login import login_required

from application.data.flask_login import check_is_admin_or_exit
from application.data.project_ids import ProjectId
from banners.data.daily.daily_banners_repository import paginate_daily_banners

daily_banners_blueprint = Blueprint('daily_banners', __name__)

@daily_banners_blueprint.route('/be/dashboard/daily_banners')
@login_required
def daily_banners_list():
    if not check_is_admin_or_exit(ProjectId.BANNERS_EDITOR):
        return

    page = request.args.get('page', 1, type=int)
    return render_template('daily_banners_list.html',
                           pagination=paginate_daily_banners(page),
                           page=page)