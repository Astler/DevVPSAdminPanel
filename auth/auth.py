from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from application import app_sqlite_db, User, sign_up_enabled

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login')
def login():
    return render_template('login.html', sign_up_enabled=sign_up_enabled)


@auth_blueprint.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

    login_user(user, remember=remember)
    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('main.profile'))


@auth_blueprint.route('/signup')
def signup():
    if sign_up_enabled:
        return render_template('signup.html', sign_up_enabled=sign_up_enabled)
    else:
        return render_template('signup_disabled.html', sign_up_enabled=sign_up_enabled)


@auth_blueprint.route('/signup', methods=['POST'])
def signup_post():
    if not sign_up_enabled:
        return
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    app_sqlite_db.session.add(new_user)
    app_sqlite_db.session.commit()

    return redirect(url_for('auth.login'))


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
