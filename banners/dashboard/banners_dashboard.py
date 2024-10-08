from flask import Blueprint, render_template, current_app
from flask_login import login_required

from admin.data.flask_login import check_is_admin_or_exit
from admin.data.project_ids import ProjectId
from banners.api.v2.common.banners_commands import get_daily_banner
from banners.data.actions.actions_repository import paginate_actions
from banners.data.mapping.banners_mapping import get_last_mapping_update, count_mapped_banners
from banners.data.messed_validator.messed_banners import messed_banners_info, find_messed_banners
from banners.data_old.banner_image_generator import get_image_data_url_by_id

dashboard_blueprint = Blueprint('dashboard_blueprint', __name__)


@dashboard_blueprint.route('/be/dashboard')
@login_required
def banners_dashboard():
    if not check_is_admin_or_exit(ProjectId.BANNERS_EDITOR):
        return

    daily_banner_data = get_daily_banner()

    if not daily_banner_data:
        return render_template('banners_dashboard.html', banner_data=None)

    messed = messed_banners_info()

    from banners.data.admin_repository import count_admins
    return render_template(
        'banners_dashboard.html',
        sign_up_enabled=current_app.config['SIGN_UP_ENABLED'],
        daily_banner_url=get_image_data_url_by_id(daily_banner_data.daily_banner_id),
        daily_banner_id=daily_banner_data.daily_banner_id,
        messed_banners=len(messed.banners) if messed is not None else "No messed banners data_old found!",
        messed_banners_update_time=messed.formatted_time() if messed is not None else "-- -- --",
        last_mapping_time=get_last_mapping_update(),
        total_banners=count_mapped_banners(),
        admin_logs=paginate_actions(1).items,
        admins_count=count_admins()
    )


@dashboard_blueprint.route('/be/find_messed_banners', methods=['GET'])
def be_check_empty_patterns():
    return find_messed_banners()