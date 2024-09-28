import config
from admin.data.project_fields import ProjectsFields
from admin.data.project_ids import ProjectsId
from application import get_db


def get_admins_by_project_id(project_id: ProjectsId) -> []:
    db = get_db(config.PROJECT_ID)
    admins = db.collection(ProjectsFields.ADMINS.value).document(project_id.value).get().to_dict()
    return admins.get(ProjectsFields.EMAILS.value, [])
