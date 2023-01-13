import os
import json
from github import Github, GithubIntegration, enable_console_debug_logging
from config import Config
from typing import AnyStr, Dict, List, Union
from datetime import datetime

DEFAULT_REPO = f"{Config.GITHUB_KARMA_OWNER}/{Config.GITHUB_KARMA_REPO}"

# Uncomment to enable extensive logging
# enable_console_debug_logging()

def get_token() -> Github:
    """
    Get a token for the github integration.
    """
    # Read the bot certificate
    with open(
            f"{Config.CERT_DIR_PATH}{Config.GITHUB_KARMA_CERT_FILENAME}",
            'r'
    ) as cert_file:
        app_key = cert_file.read()

    # Create a GitHub integration instance
    git_integration = GithubIntegration(
        Config.GITHUB_APP_ID,
        app_key,
    )

    # return Github object
    return Github(
        login_or_token=git_integration.get_access_token(
            git_integration.get_installation(
                Config.GITHUB_KARMA_OWNER, 
                Config.GITHUB_KARMA_REPO).id
        ).token
    )


# IDENTITIES
def get_identities() -> Union[Dict, None]:
    """ Get the identities from the github repo. """
    try:
        git_connection = get_token()
        repo = git_connection.get_repo(DEFAULT_REPO)
        content = repo.get_contents(f"{Config.GITHUB_KARMA_DATA_DIR}/{Config.GITHUB_KARMA_CONTRIBUTORS_FILENAME}")
        return json.loads(content.decoded_content.decode())
    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")
        return None


def push_identities(identities: Dict) -> None:
    """
    Pushes the identities to github.
    :param identities: updated json file.
    """
    try:
        git_connection = get_token()
        repo = git_connection.get_repo(DEFAULT_REPO)
        content = repo.get_contents(f"{Config.GITHUB_KARMA_DATA_DIR}/{Config.GITHUB_KARMA_CONTRIBUTORS_FILENAME}")
        repo.update_file(content.path, "updated identity", json.dumps(identities, indent=2), content.sha)
    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")


# ISSUES
def get_issues(repository: AnyStr=DEFAULT_REPO, state: AnyStr="all") -> Union[List, None]:
    """
    Get issues from a github repo.
    """
    try:
        git_connection = get_token()
        repo = git_connection.get_repo(repository)
        return repo.get_issues(state=state)
    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")
        return None


# PAYMENTS
def get_payments() -> Union[List, None]:
    """
    Get all payments from the github repo.
    """
    try:
        git_connection = get_token()
        repo = git_connection.get_repo(DEFAULT_REPO)
        content = repo.get_contents(f"{Config.GITHUB_KARMA_DATA_DIR}/{Config.GITHUB_KARMA_CONTRIBUTORS_FILENAME}")
        return json.loads(content.decoded_content.decode())
    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")
        return None


def push_payments(payments: Dict) -> None:
    """
    Pushes the payments to github.
    :param payments: updated json file.
    """
    try:
        git_connection = get_token()
        repo = git_connection.get_repo(DEFAULT_REPO)
        content = repo.get_contents(f"{Config.GITHUB_KARMA_DATA_DIR}/{Config.GITHUB_KARMA_CONTRIBUTORS_FILENAME}")
        repo.update_file(content.path, "updated payments", json.dumps(payments, indent=2), content.sha)
    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")
