import os
import json
from github import Github, GithubIntegration, enable_console_debug_logging
from config import Config

# Read the bot certificate
with open(
        Config.GITHUB_CERT_FILE_PATH,
        'r'
) as cert_file:
    app_key = cert_file.read()

# Create a GitHub integration instance
git_integration = GithubIntegration(
    Config.GITHUB_APP_ID,
    app_key,
)

# repo URI suffix
repo_uri_suffix = f"{Config.GITHUB_OWNER}/{Config.GITHUB_KARMA_REPO}"

# Uncomment to enable extensive logging
# enable_console_debug_logging()

def get_token():
    """
    Get a token for the github integration.
    """
    return Github(
        login_or_token=git_integration.get_access_token(
            git_integration.get_installation(
                Config.GITHUB_OWNER, 
                Config.GITHUB_KARMA_REPO).id
        ).token
    )


# IDENTITIES
def get_identities():
    """ Get the identities from the github repo. """
    git_connection = get_token()

    repo = git_connection.get_repo(repo_uri_suffix)
    contributors = repo.get_contents(f"{Config.GITHUB_DATA_DIR}/{Config.CONTRIBUTORS_FILENAME}")
    return json.loads(contributors.decoded_content.decode())


def push_identities(identities):
    """
    Pushes the identities to github.
    :param identities: updated json file.
    """
    git_connection = get_token()
    repo = git_connection.get_repo(repo_uri_suffix)
    readme = repo.get_contents(f"{Config.GITHUB_DATA_DIR}/{Config.CONTRIBUTORS_FILENAME}")  # change this location after testing phase
    repo.update_file(readme.path, "updated identity", json.dumps(identities, indent=2), readme.sha)


# ISSUES
def get_issues():
    """
    Get all issues from the github repo.
    """
    git_connection = get_token()

    repo = git_connection.get_repo(repo_uri_suffix)
    for i in repo.get_issues():
        print(i.body)
    return repo.get_issues()


def get_closed_issues():
    git_connection = get_token()

    repo = git_connection.get_repo(repo_uri_suffix)
    for i in repo.get_issues(state="closed"):
        print(i.body)
    return repo.get_issues(state="closed")


# PAYMENTS
def get_payments():
    """
    Get all payments from the github repo.
    """
    git_connection = get_token()

    repo = git_connection.get_repo(repo_uri_suffix)
    readme = repo.get_contents("data/payments_test.json")  # change this location after testing phase
    return json.loads(readme.decoded_content.decode())


def push_payments(payments):
    """
    Pushes the payments to github.
    :param payments: updated json file.
    """
    git_connection = get_token()
    repo = git_connection.get_repo(repo_uri_suffix)
    readme = repo.get_contents("data/payments_test.json")  # change this location after testing phase
    repo.update_file(readme.path, "updated payments", json.dumps(payments, indent=2), readme.sha)
