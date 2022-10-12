from flask import Flask, request, jsonify

app = Flask(__name__)

from banners.banners_commands import app


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
