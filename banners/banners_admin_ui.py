import time

import firebase_admin
import simplejson as json
from firebase_admin import credentials, firestore
from flask import Blueprint
import os

from banners.data import get_cer_data, check_file_by_path, get_last_update_time, set_last_update_time, \
    send_telegram_msg_to_me
from config import PROJECT_ID, BE_BANNERS_MAP, BE_MAP_UPDATE_HOURS

banners_ui_blueprint = Blueprint('banners_ui', __name__)


@banners_ui_blueprint.route('/be_admin', methods=['GET'])
def get_map_version():
    return str(get_last_update_time())
