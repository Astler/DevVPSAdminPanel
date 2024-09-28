from application import get_db
from cat.utils.telegram_utils import send_telegram_msg_to_me
from config import MC_PROJECT_ID

__firestore_client = None

banners_folder = u'shared_banners'

def get_banners_editor_firestore():
    global __firestore_client

    if __firestore_client is None:
        __firestore_client = get_db(MC_PROJECT_ID)
        send_telegram_msg_to_me("Loaded BE firestore client!")

    return __firestore_client


def get_be_firestore_collection(collection_name: str):
    return get_banners_editor_firestore().collection(collection_name)


def get_be_shared():
    return get_banners_editor_firestore().collection(banners_folder)

def get_shared_banner_ref(banner_id: str):
    return get_be_shared().document(banner_id)

def get_shared_banner_data(banner_id: str):
    return get_shared_banner_ref(banner_id).get().to_dict()