from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user

from application.data.firestore_admin_content import is_admin
from application.data.project_ids import ProjectId

profile_blueprint = Blueprint('profile_blueprint', __name__)

@profile_blueprint.route('/profile')
@login_required
def profile():
    is_be_admin = is_admin(current_user.email, ProjectId.BANNERS_EDITOR)
    is_core_admin = is_admin(current_user.email, ProjectId.PRESSF_CORE)
    is_drink_lab_admin = is_admin(current_user.email, ProjectId.DRINK_LAB)

    return render_template('profile.html',
                           name=current_user.name,
                           sign_up_enabled=current_app.config['SIGN_UP_ENABLED'],
                           is_banner_admin=is_be_admin,
                           is_core_admin=is_core_admin,
                           is_drink_lab_admin=is_drink_lab_admin)
