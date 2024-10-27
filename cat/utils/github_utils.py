import json

from github import GithubException

from config import A_PATH
from application.loader import repository


def load_firebase_certificate(path):
    return load_git_json(path)


def get_a_list() -> [str]:
    return load_git_json(A_PATH)


###
# Common
###

def load_git_json(path: str):
    file_content = load_git_file(path)

    if len(file_content) == 0:
        return {}

    try:
        json_content = json.loads(file_content)
    except GithubException:
        json_content = {}

    return json_content


def load_git_file(path: str) -> str:
    try:
        file = repository.get_contents(path)
        file_content = str(file.decoded_content.decode())

    except GithubException:
        file_content = ""

    return file_content
