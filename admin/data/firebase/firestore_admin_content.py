import config
from admin.data.project_fields import ProjectsFields
from admin.data.project_ids import ProjectId
from application import get_db


def get_admins_by_project_id(project_id: ProjectId) -> []:
    db = get_db(config.PROJECT_ID)
    admins = db.collection(ProjectsFields.ADMINS.value).document(project_id.value).get().to_dict()
    return admins.get(ProjectsFields.EMAILS.value, [])


def is_admin(email: str, project_id: ProjectId) -> bool:
    admins = get_admins_by_project_id(project_id)
    return email in admins
