from datetime import datetime

from flask import Flask, current_app
from flask_apscheduler import APScheduler
from flask_login import LoginManager

from banners.scheduled.banners_editor_scheduled import check_for_daily_banner
from cat.utils.telegram_utils import send_telegram_msg_to_me
from core.data.user_data import User
from core.dependencies import app_sqlite_db, migrate
from core.firebase import firebase_connect_multiple

send_telegram_msg_to_me("Запуск приложения!")

app = None

import os

file_path = os.path.abspath(os.getcwd()) + "/app/instance/db.sqlite"

def scheduled_task():
    #check_for_daily_banner()
    current_app.logger.info(f"Performing scheduled task at {datetime.now()}")

def run_scheduled_tasks():
    print("Running all scheduled tasks on start...")
    scheduled_task()
    # Add any other scheduled tasks here
    print("Finished running scheduled tasks")



def create_app():
    global app
    app = Flask(__name__, instance_path='/instance')

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////instance/db.sqlite'

    app.config['SIGN_UP_ENABLED'] = True

    os.makedirs(app.instance_path, exist_ok=True)

    app_sqlite_db.init_app(app)
    migrate.init_app(app, app_sqlite_db)

    from banners.api.v2.common.banners_commands import banners_api_blueprint
    app.register_blueprint(banners_api_blueprint)

    from banners.api.v2.admin.admin_commands import banners_admin
    app.register_blueprint(banners_admin)

    from banners.api.v2.internal.internal_commands import admins_internal
    app.register_blueprint(admins_internal)

    from auth.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from main.main import main_blueprint
    app.register_blueprint(main_blueprint)

    from banners.dashboard.banners_dashboard import dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)

    from banners.dashboard.deleted_banners_list import deleted_banners_blueprint
    app.register_blueprint(deleted_banners_blueprint)

    from banners.dashboard.daily_banners_list import daily_banners_blueprint
    app.register_blueprint(daily_banners_blueprint)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        app_sqlite_db.create_all()

    firebase_connect_multiple()

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    scheduler.add_job(id='daily_task', func=scheduled_task, trigger='cron', hour=0, minute=0)

    with app.app_context():
        run_scheduled_tasks()

    return app
