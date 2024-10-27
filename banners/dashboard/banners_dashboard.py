from datetime import datetime

from flask import Blueprint, render_template, url_for, jsonify
from flask_login import login_required

from admin.data.flask_login import check_is_admin_or_exit
from admin.data.project_ids import ProjectId
from banners.api.v2.common.banners_commands import get_daily_banner
from banners.data.actions.actions_repository import paginate_actions
from banners.data.mapping.banners_mapping import get_last_mapping_update, count_mapped_banners
from banners.data_old.banner_image_generator import get_image_data_url_by_id

dashboard_blueprint = Blueprint('dashboard_blueprint', __name__)


# Add new endpoint for async banner count
@dashboard_blueprint.route('/be/dashboard/banner_count')
@login_required
def get_banner_count():
    if not check_is_admin_or_exit(ProjectId.BANNERS_EDITOR):
        return jsonify({'error': 'Unauthorized'}), 403

    total = count_mapped_banners()
    return jsonify({'count': total})


@dashboard_blueprint.route('/be/dashboard')
@login_required
def banners_dashboard():
    if not check_is_admin_or_exit(ProjectId.BANNERS_EDITOR):
        return

    daily_banner_data = get_daily_banner()

    if not daily_banner_data:
        return render_template('banners_dashboard.html', banner_data=None)

    buttons = [
        {
            'label': 'All Daily Banners',
            'url': url_for('daily_banners.daily_banners_list'),
        },
        {
            'label': 'Deleted',
            'url': url_for('deleted_banners.deleted_banners_list'),
        },
        {
            'label': 'Admins Actions',
            'url': url_for('admins_banners.admins_actions_list'),
        },
    ]

    last_mapping_time = datetime.fromtimestamp(get_last_mapping_update() / 1000).strftime('%Y-%m-%d %H:%M:%S')

    from banners.data.admin_repository import count_admins
    return render_template(
        'banners_dashboard.html',
        daily_banner_url=get_image_data_url_by_id(daily_banner_data.daily_banner_id),
        daily_banner_id=daily_banner_data.daily_banner_id,
        last_mapping_time=last_mapping_time,
        total_banners=0,
        admin_logs=paginate_actions(1).items,
        admins_count=count_admins(),
        buttons=buttons
    )
