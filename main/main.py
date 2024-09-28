from flask import Blueprint, render_template, current_app, redirect, url_for
from flask_login import login_required, current_user

from admin.data.firebase.firestore_admin_content import is_admin
from admin.data.project_ids import ProjectId

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    return render_template('index.html', sign_up_enabled=current_app.config['SIGN_UP_ENABLED'])


@main_blueprint.route('/profile')
@login_required
def profile():
    is_be_admin = is_admin(current_user.email, ProjectId.BANNERS_EDITOR)
    return render_template('profile.html',
                           name=current_user.name,
                           sign_up_enabled=current_app.config['SIGN_UP_ENABLED'],
                           is_banner_admin=is_be_admin)
