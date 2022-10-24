import json

from github import GithubException

from config import CERT_PATH
from loader import repository


def get_cer_data():
    try:
        file = repository.get_contents(CERT_PATH)
        contents = file.decoded_content.decode()
        cer = json.loads(contents)
    except GithubException:
        cer = {}

    return cer
