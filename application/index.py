from flask import Blueprint, render_template, current_app, redirect, url_for
from flask_login import current_user

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile_blueprint.profile'))
    return render_template('index.html', sign_up_enabled=current_app.config['SIGN_UP_ENABLED'])

