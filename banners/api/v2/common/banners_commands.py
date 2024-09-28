from flask import Blueprint, request

from application.base_response import BaseResponse
from banners.data.daily.daily_banners_repository import generate_daily_banners_response, get_daily_banner
from banners.data.mapping.banners_mapping import get_mapping
from banners.data_old.be_server_saves import get_banners_settings

banners_api_blueprint = Blueprint('banners_api', __name__)


@banners_api_blueprint.route('/be/api/daily_banners', methods=['GET', 'POST'])
def get_paged_banners():
    return generate_daily_banners_response(request)


@banners_api_blueprint.route('/be_daily_banners_list', methods=['GET', 'POST'])
def get_paged_banners_old():
    return get_paged_banners()

@banners_api_blueprint.route('/be/api/daily_banner', methods=['GET', 'POST'])
def get_daily_banner_json():
    request_parameters = request.args.to_dict()
    banner = get_daily_banner(request_parameters)

    if banner is None:
        return BaseResponse(False, "No banner available for the specified date range!",
                            request_parameters).to_response()

    return str(banner.to_json()).replace("\'", "\"")


@banners_api_blueprint.route('/be/daily_banner', methods=['GET', 'POST'])
def get_daily_banner_json_old():
    return get_daily_banner_json()


@banners_api_blueprint.route('/be/api/settings', methods=['GET'])
def get_settings():
    return get_banners_settings()


@banners_api_blueprint.route('/be/settings', methods=['GET'])
def get_settings_old():
    return get_settings()


#
# new commands
#

@banners_api_blueprint.route('/be/mapping', methods=['GET'])
def get_banners_mapping():
    return get_mapping()


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
