from datetime import datetime

from flask import current_app
from flask_apscheduler import APScheduler

from application import create_app
from banners.scheduled.banners_editor_scheduled import check_for_daily_banner

if __name__ == "__main__":
    app = create_app()

    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
        return datetime.fromtimestamp(value).strftime(format)

    print("Starting the application...")
    app.run(host='0.0.0.0', debug=True, port=49999)