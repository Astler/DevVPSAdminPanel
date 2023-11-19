from flask import Blueprint, Response, request

from banners.data.admin_actions import delete_banner, add_to_daily

banners_admin = Blueprint('banners_admin', __name__)


@banners_admin.route('/be/delete_banner', methods=['GET', 'POST'])
def delete_banner_by_admin() -> Response:
    return delete_banner(request)


@banners_admin.route('/be/to_daily_queue', methods=['GET', 'POST'])
def add_to_daily_queue() -> Response:
    return add_to_daily(request)
