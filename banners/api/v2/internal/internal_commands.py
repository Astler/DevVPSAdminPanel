from flask import Blueprint, Response
from flask_login import login_required

from application.data.firestore_admin_content import get_admins_by_project_id
from application.data.project_ids import ProjectId

admins_internal = Blueprint('admins_internal', __name__)

@admins_internal.route('/be/api/internal/admins', methods=['GET', 'POST'])
@login_required
def get_admins() -> Response:
    return get_admins_by_project_id(ProjectId.BANNERS_EDITOR)