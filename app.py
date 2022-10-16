import firebase_admin
from firebase_admin import credentials
from flask import Flask, request

from banners.banners_commands import banners_api
from banners.data import send_telegram_msg_to_me, get_cer_data
from config import PROJECT_ID

send_telegram_msg_to_me("Запуск приложения!")

app = Flask(__name__)

app.register_blueprint(banners_api)

send_telegram_msg_to_me("Подключаюсь к Firebase!")

cred = credentials.Certificate(get_cer_data())

firebase_admin.initialize_app(cred, {
    'projectId': PROJECT_ID,
})


@app.route('/')
def index():
    return 'Hello my friend!'


@app.route('/me', methods=['GET'])
def me():
    return """{"name":"astler!"}"""


@app.route('/test_get', methods=['GET'])
def search():
    args = request.args
    return args


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=49999)
