from admin.data.firebase.firestore_admin_content import get_admins_by_project_id
from admin.data.project_ids import ProjectsId
from application.base_response import BaseResponse


def is_banner_admin(email: str) -> bool:
    admins = get_admins_by_project_id(ProjectsId.BANNERS_EDITOR)
    return email in admins


def count_admins() -> int:
    return len(get_admins_by_project_id(ProjectsId.BANNERS_EDITOR))


def admin_validation(request_parameters: dict) -> BaseResponse:
    if not request_parameters.__contains__("admin"):
        return BaseResponse(False, "You need to provide your admin id to perform this action",
                            request_parameters)

    if not request_parameters.__contains__("id"):
        return BaseResponse(False, "Do you forgot to add banner id?", request_parameters)

    admins = get_admins_by_project_id(ProjectsId.BANNERS_EDITOR)
    admin_id = request_parameters["admin"]

    if not admins.__contains__(admin_id):
        return BaseResponse(False, f"User {admin_id} is not admin!", request_parameters)

    return BaseResponse(True, request_data=request_parameters)
