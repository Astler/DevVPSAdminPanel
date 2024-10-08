import json
from typing import Dict

from flask import Response
from flask_sqlalchemy.pagination import Pagination

from core.dependencies import app_sqlite_db
from application.base_response import BaseResponse
from banners.data.actions.action_item import AdminActionModel, AdminAction
from banners.data.admin_repository import admin_validation
from banners.data.firebase.firestore_repository import get_shared_banner_ref
from banners.data_old.banner_image_generator import get_layers_from_web
from banners.types.deleted_banner import DeletedBannerModel, DeletedBannerModelEncoder
from config import BE_PAGE_SIZE


def total_deleted_banners():
    return app_sqlite_db.session.query(DeletedBannerModel).count()


def paginate_deleted_banners(page=1) -> Pagination:
    pagination = app_sqlite_db.session.query(DeletedBannerModel).paginate(
        page=page, per_page=BE_PAGE_SIZE, error_out=False
    )

    for banner in pagination.items:
        if banner.layers is None:
            banner.layers = json.dumps(get_layers_from_web(banner.id), ensure_ascii=False,
                                       cls=DeletedBannerModelEncoder)
            app_sqlite_db.session.add(banner)

    app_sqlite_db.session.commit()

    pagination.items = [banner.to_ui_info() for banner in pagination.items]

    return pagination


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
