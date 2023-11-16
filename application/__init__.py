import firebase_admin
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from firebase_admin import credentials
from flask_login import LoginManager, UserMixin

from application.github_utils import get_cer_data
from cat.utils.telegram_utils import send_telegram_msg_to_me
from config import PROJECT_ID

send_telegram_msg_to_me("Запуск приложения!")

db = SQLAlchemy()

sign_up_enabled = True


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


def create_app():
    global app
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    from banners.banners_commands import banners_api_blueprint
    app.register_blueprint(banners_api_blueprint)

    from banners.banners_admin_ui import banners_ui_blueprint
    app.register_blueprint(banners_ui_blueprint)

    from auth.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from main.main import main_blueprint
    app.register_blueprint(main_blueprint)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()


def firebase_connect():
    send_telegram_msg_to_me("Подключаюсь к Firebase!")

    cred = credentials.Certificate(get_cer_data())

    firebase_admin.initialize_app(cred, {
        'projectId': PROJECT_ID,
    })


create_app()
firebase_connect()
