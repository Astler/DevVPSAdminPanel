from flask import Blueprint, render_template
from flask_login import login_required, current_user

from application import sign_up_enabled
main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    return render_template('index.html', sign_up_enabled=sign_up_enabled)


@main_blueprint.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, sign_up_enabled=sign_up_enabled)