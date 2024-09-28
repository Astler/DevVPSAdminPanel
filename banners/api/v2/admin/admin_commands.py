from flask import Blueprint, Response, request

from banners.data.daily.daily_banners_repository import add_to_daily
from banners.data.delete.deleting_repository import delete_banner

banners_admin = Blueprint('banners_admin', __name__)


@banners_admin.route('/be/api/delete_banner', methods=['GET', 'POST'])
def delete_banner_by_admin() -> Response:
    return delete_banner(request)

@banners_admin.route('/be/api/mock_delete_banner', methods=['GET', 'POST'])
def mock_delete_banner_by_admin() -> Response:
    return delete_banner(request, True)


@banners_admin.route('/be/api/to_daily_queue', methods=['GET', 'POST'])
def add_to_daily_queue() -> Response:
    return add_to_daily(request)