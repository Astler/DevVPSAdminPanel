from flask import Blueprint

from banners.data import get_last_update_time

banners_ui_blueprint = Blueprint('banners_ui', __name__)


@banners_ui_blueprint.route('/be_admin', methods=['GET'])
def get_map_version():
    return str(get_last_update_time())
