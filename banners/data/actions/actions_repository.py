from application import app_sqlite_db
from banners.data.actions.action_item import AdminActionModel, AdminAction
from banners.data.firebase.banner_firebase_item import BannerFirebaseItem
from banners.data_old.banner_image_generator import get_image_data_url


def get_all_actions() -> []:
    actions = app_sqlite_db.session.query(AdminActionModel).order_by(AdminActionModel.record_id.desc()).all()

    result = []

    for action in actions:
        banner = BannerFirebaseItem.from_json(action.action_data)

        if banner is not None:
            action.banner_url = get_image_data_url(banner.layers, 1)

        action.translated_action = str(AdminAction.get_action_by_value(action.action).name)

        result.append(action)

    return result
