from flask import Blueprint, Response
from flask_login import login_required

from admin.data.firebase.firestore_admin_content import get_admins_by_project_id
from admin.data.project_ids import ProjectsId

admins_internal = Blueprint('admins_internal', __name__)

@admins_internal.route('/be/api/internal/admins', methods=['GET', 'POST'])
@login_required
def get_admins() -> Response:
    return get_admins_by_project_id(ProjectsId.BANNERS_EDITOR)