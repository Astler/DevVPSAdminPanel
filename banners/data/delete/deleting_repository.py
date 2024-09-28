import json
import time
from typing import Dict

from flask import Response

from application import app_sqlite_db
from application.base_response import BaseResponse
from banners.data.actions.action_item import AdminActionModel, AdminAction
from banners.data.admin_repository import admin_validation
from banners.data.firebase.firestore_repository import get_shared_banner_ref
from banners.types.deleted_banner import DeletedBannerModel, DeletedBannerModelEncoder
from cat.utils.telegram_utils import send_telegram_msg_to_me
from config import BE_PAGE_SIZE


def get_deleted_banners(page=0):
    return (
        app_sqlite_db.session.query(DeletedBannerModel)
        .order_by(DeletedBannerModel.date.desc())
        .offset(page * BE_PAGE_SIZE)
        .limit(BE_PAGE_SIZE)
        .all()
    )


def delete_banner(request, mock: bool = False) -> Response:
    content = request.args.to_dict()

    if not (check_result := admin_validation(content)).success:
        return check_result.to_response()

    admin_id = content["admin"]
    banner_id = content["id"]

    banner_ref = get_shared_banner_ref(banner_id)
    banner_data = banner_ref.get().to_dict()

    if banner_data is None:
        return BaseResponse(False, f"Banner with id {banner_id} not found!", content).to_response()

    store_deleted_banner(banner_id, admin_id, banner_data)

    if not mock:
        try:
            banner_ref.delete()
        except Exception as error:
            return BaseResponse(False, str(error), content).to_response()

    return BaseResponse(True).to_response()


def store_deleted_banner(banner_id: str, admin_id: str, banner_data: Dict):
    app_sqlite_db.session.add(DeletedBannerModel.build(
        banner_id=banner_id,
        admin_id=admin_id,
        banner_data=banner_data
    ))

    app_sqlite_db.session.add(AdminActionModel.build(
        admin_id=admin_id,
        action_info=banner_data,
        action=AdminAction.Deleted
    ))

    app_sqlite_db.session.commit()
