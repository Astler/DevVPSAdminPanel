from flask import Blueprint, render_template, current_app, redirect, url_for
from flask_login import login_required, current_user

from banners.data.admin_repository import is_banner_admin

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    return render_template('index.html', sign_up_enabled=current_app.config['SIGN_UP_ENABLED'])


@main_blueprint.route('/profile')
@login_required
def profile():
    is_admin = is_banner_admin(current_user.email)
    return render_template('profile.html',
                           name=current_user.name,
                           sign_up_enabled=current_app.config['SIGN_UP_ENABLED'],
                           is_banner_admin=is_admin)
