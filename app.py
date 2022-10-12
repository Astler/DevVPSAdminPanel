from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello to Flask!'


@app.route('/me', methods=['GET'])
def me():
    return """{"name":"astler!"}"""


@app.route('/test_get', methods=['GET'])
def search():
    args = request.args
    return args


@app.route('/foo', methods=['POST'])
def foo():
    data = request.json
    return jsonify(data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=49999)
