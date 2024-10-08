import firebase_admin
from firebase_admin import credentials, firestore

from cat.utils.github_utils import load_firebase_certificate
from cat.utils.telegram_utils import send_telegram_msg_to_me
from config import PROJECT_ID, CERT_PATH, MC_PROJECT_ID, MC_CERT_PATH


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
