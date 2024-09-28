import json
import time

from flask import Response

from application import app_sqlite_db
from application.base_response import BaseResponse
from banners.data.admin_repository import admin_validation
from banners.data.firebase.firestore_repository import get_shared_banner_ref
from banners.types.deleted_banner import DeletedBannerItem
from cat.utils.telegram_utils import send_telegram_msg_to_me
from config import BE_PAGE_SIZE


def get_deleted_banners(page=0) -> []:
    deleted_banners = app_sqlite_db.session.query(DeletedBannerItem).order_by(DeletedBannerItem.date.desc())

    selection = []

    last_item_index = (page + 1) * BE_PAGE_SIZE
    first_item_index = page * BE_PAGE_SIZE

    if deleted_banners.count() < last_item_index:
        last_item_index = deleted_banners.count()

    for banner in deleted_banners[first_item_index:last_item_index]:
        selection.append(banner)

    return selection


def delete_banner(request) -> Response:
    content = request.args.to_dict()

    check_result = admin_validation(content)

    if not check_result.success:
        return check_result.to_response()

    admin_id = content["admin"]
    banner_id = content["id"]

    banner_ref = get_shared_banner_ref(banner_id)
    banner_data = banner_ref.get().to_dict()

    if banner_data is None:
        return BaseResponse(False, f"Banner with id {banner_id} not found!", content).to_response()

    send_telegram_msg_to_me(f"Admin with id {admin_id} requested deletion of this banner {banner_id}\n\n{banner_data}")

    app_sqlite_db.session.add(DeletedBannerItem(id=admin_id, content=json.dumps(banner_data), date=time.time()))
    app_sqlite_db.session.commit()

    try:
        banner_ref.delete()
    except Exception as error:
        return BaseResponse(False, str(error), content).to_response()

    return BaseResponse(True).to_response()
