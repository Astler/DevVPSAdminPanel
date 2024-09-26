from flask import Blueprint, request

from application.base_response import BaseResponse
from banners.data.banners_mapping import get_mapping
from banners.data.be_server_saves import get_banners_settings
from banners.data.daily_banners import get_daily_banner, get_all_daily_banners
from banners.data.messed_banners import find_messed_banners

banners_api_blueprint = Blueprint('banners_api', __name__)


@banners_api_blueprint.route('/be/daily_banners', methods=['GET', 'POST'])
def get_paged_banners():
    return get_all_daily_banners(request)


@banners_api_blueprint.route('/be/daily_banner', methods=['GET', 'POST'])
def get_daily_banner_json():
    request_parameters = request.args.to_dict()
    banner = get_daily_banner(request_parameters)

    if banner is None:
        return BaseResponse(False, "No banner available for the specified date range!",
                            request_parameters).to_response()

    return str(banner.to_json()).replace("\'", "\"")


@banners_api_blueprint.route('/be/settings', methods=['GET'])
def get_settings():
    return get_banners_settings()


#
# new commands
#

@banners_api_blueprint.route('/be/mapping', methods=['GET'])
def get_banners_mapping():
    return get_mapping()


@banners_api_blueprint.route('/be/find_messed_banners', methods=['GET'])
def be_check_empty_patterns():
    return find_messed_banners()


#
# old and legacy
# todo remove later
#

@banners_api_blueprint.route('/be_map', methods=['GET'])
def get_old_banners_mapping():
    return get_banners_mapping()


@banners_api_blueprint.route('/be_settings', methods=['GET'])
def get_old_settings():
    return get_settings()


@banners_api_blueprint.route('/be_daily_banners_list', methods=['GET', 'POST'])
def get_old_paged_banners():
    return get_paged_banners()
