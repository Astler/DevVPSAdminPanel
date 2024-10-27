from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from application import User
from core.dependencies import app_sqlite_db
from functools import wraps
import re

auth_blueprint = Blueprint('auth', __name__)


def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!_@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Implement rate limiting logic here
        return func(*args, **kwargs)

    return wrapper


@auth_blueprint.route('/login', methods=['GET', 'POST'])
@rate_limit
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile_blueprint.profile'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('profile_blueprint.profile'))

        flash('Invalid email or password', 'error')

    return render_template('login.html', sign_up_enabled=current_app.config['SIGN_UP_ENABLED'])


@auth_blueprint.route('/signup', methods=['GET', 'POST'])
@rate_limit
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('profile_blueprint.profile'))

    if not current_app.config['SIGN_UP_ENABLED']:
        return render_template('signup_disabled.html')

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        if not validate_password(password):
            flash('Password does not meet complexity requirements', 'error')
            return render_template('signup.html')

        if User.query.filter_by(email=email).first():
            flash('Email address already exists', 'error')
            return render_template('signup.html')

        new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'))
        app_sqlite_db.session.add(new_user)
        app_sqlite_db.session.commit()

        flash('Account created successfully', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', sign_up_enabled=current_app.config['SIGN_UP_ENABLED'])


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))
