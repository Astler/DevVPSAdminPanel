from firebase_admin import firestore

from cat.utils.telegram_utils import send_telegram_msg_to_me

__firestore_client = None


def get_firestore_client():
    global __firestore_client

    if __firestore_client is None:
        __firestore_client = firestore.client()
        send_telegram_msg_to_me("Loaded firestore client!")

    return __firestore_client


def get_firestore_collection(collection_name: str):
    return get_firestore_client().collection(collection_name)
