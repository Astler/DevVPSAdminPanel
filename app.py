from flask import Flask
import os.path

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello to Flask!'


@app.route('/me')
def me():
    return "astler!"


@app.route('/.well-known/pki-validation/948281C097CA441852C3AB70F8720614.txt')
def verification():
    read = open("948281C097CA441852C3AB70F8720614.txt", 'r')
    data = read.read()
    read.close()
    return data


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)
