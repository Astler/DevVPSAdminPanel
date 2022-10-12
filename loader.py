from github import Github

from config import GITHUB_TOKEN, GITHUB_REPO

github = Github(GITHUB_TOKEN)
repository = github.get_user().get_repo(GITHUB_REPO)