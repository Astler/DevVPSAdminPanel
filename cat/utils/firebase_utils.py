from firebase_admin import firestore

from application import get_db
from cat.utils.telegram_utils import send_telegram_msg_to_me
from config import MC_PROJECT_ID

__firestore_client = None


def get_mc_firestore_client():
    global __firestore_client

    if __firestore_client is None:
        __firestore_client = get_db(MC_PROJECT_ID)
        send_telegram_msg_to_me("Loaded firestore client!")

    return __firestore_client


def get_mc_firestore_collection(collection_name: str):
    return get_mc_firestore_client().collection(collection_name)
