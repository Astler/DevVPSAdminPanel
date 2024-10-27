from datetime import datetime

from application import create_app

if __name__ == "__main__":
    app = create_app()

    print("Starting the application...")
    app.run(host='0.0.0.0', debug=True, port=49999)