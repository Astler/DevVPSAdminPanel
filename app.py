from datetime import datetime

from application import create_app

if __name__ == "__main__":
    app = create_app()

    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
        return datetime.fromtimestamp(value).strftime(format)

    app.run(host='0.0.0.0', debug=True, port=49999)
