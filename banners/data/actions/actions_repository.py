from flask_sqlalchemy.pagination import Pagination

from banners.data.actions.action_item import AdminActionModel
from config import BE_PAGE_SIZE
from core.dependencies import app_sqlite_db


def paginate_actions(page=1) -> Pagination:
    pagination = app_sqlite_db.session.query(AdminActionModel).order_by(AdminActionModel.record_id.desc()).paginate(
        page=page, per_page=BE_PAGE_SIZE, error_out=False
    )

    pagination.items = [action.to_ui_info() for action in pagination.items]

    return pagination