import firebase_admin
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from firebase_admin import credentials, firestore
from flask_login import LoginManager, UserMixin

from cat.utils.github_utils import load_firebase_certificate
from cat.utils.telegram_utils import send_telegram_msg_to_me
from config import PROJECT_ID, CERT_PATH, MC_PROJECT_ID, MC_CERT_PATH

send_telegram_msg_to_me("Запуск приложения!")

app_sqlite_db = SQLAlchemy()
app = None

import os

file_path = os.path.abspath(os.getcwd()) + "/app/instance/db.sqlite"


class User(UserMixin, app_sqlite_db.Model):
    id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    email = app_sqlite_db.Column(app_sqlite_db.String(100), unique=True)
    password = app_sqlite_db.Column(app_sqlite_db.String(100))
    name = app_sqlite_db.Column(app_sqlite_db.String(1000))


def create_app():
    global app
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    app.config['SIGN_UP_ENABLED'] = True

    app_sqlite_db.init_app(app)

    from banners.banners_commands import banners_api_blueprint
    app.register_blueprint(banners_api_blueprint)

    from banners.admin_commands import banners_admin
    app.register_blueprint(banners_admin)

    from auth.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from main.main import main_blueprint
    app.register_blueprint(main_blueprint)

    from banners.ui.banners_dashboard import dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        app_sqlite_db.create_all()

    firebase_connect_multiple()

    return app


def firebase_connect_multiple():
    send_telegram_msg_to_me("Подключаюсь к нескольким проектам Firebase!")

    admin_cred = credentials.Certificate(load_firebase_certificate(CERT_PATH))
    first_app = firebase_admin.initialize_app(admin_cred, {
        'projectId': PROJECT_ID,
    }, name=PROJECT_ID)

    mc_cred = credentials.Certificate(load_firebase_certificate(MC_CERT_PATH))
    second_app = firebase_admin.initialize_app(mc_cred, {
        'projectId': MC_PROJECT_ID,
    }, name=MC_PROJECT_ID)

    return first_app, second_app


def get_db(app_name):
    return firestore.client(app=firebase_admin.get_app(name=app_name))
