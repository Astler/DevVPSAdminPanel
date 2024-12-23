from flask import redirect, url_for
from flask_login import current_user

from application.data.firestore_admin_content import is_admin
from application.data.project_ids import ProjectId


def check_is_admin_or_exit(project_id: ProjectId):
    if not is_admin(current_user.email, project_id):
        redirect(url_for('profile_blueprint.profile'))
        return False

    return True