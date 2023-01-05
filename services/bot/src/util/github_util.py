import os
import json
from github import Github, GithubIntegration

# Read the bot certificate
app_key = ""
with open(
        os.getenv(
            "GITHUB_CERT_FILE_PATH",
            "/home/user/projects/karma-bot/services/bot/.certs/karma-bot-test.2022-12-26.private-key.pem"
        ),
        'r'
) as cert_file:
    app_key = cert_file.read()
app_id = int(os.getenv("GITHUB_APP_ID", "275927"))

# Create a GitHub integration instance
git_integration = GithubIntegration(
    app_id,
    app_key,
    base_url="https://github.com/api/v3"
)

install = git_integration\
    .get_installation(
        os.getenv("GITHUB_OWNER", "Paulito123"),
        os.getenv("GITHUB_KARMA_REPO", "karma-bot")
    )

gh_repo_suffix = f"{os.getenv('GITHUB_OWNER')}/{os.getenv('GITHUB_KARMA_REPO')}"
gh_contributors_file = f"{os.getenv('GITHUB_DATA_DIR')}{os.getenv('CONTRIBUTORS_FILENAME')}"
gh_payments_file = f"{os.getenv('GITHUB_DATA_DIR')}/{os.getenv('PAYMENTS_FILENAME')}"

def get_token():
    """
    Get a token for the github integration.
    """
    return Github(
        login_or_token = git_integration.get_access_token(
            git_integration.get_installation(
                os.getenv("GITHUB_OWNER", "paulito123"),
                os.getenv("GITHUB_KARMA_REPO", "karma-bot")
                ).id
        ).token
    )


def get_issues():
    """
    Get all issues from the github repo.
    """
    # TODO Try catch
    git_connection = get_token()
    repo = git_connection.get_repo(gh_repo_suffix)

    for i in repo.get_issues():
        print(i.body)
    return repo.get_issues()


def get_identities():
    """
        Get the identities from the github repo.
    """
    # TODO Try catch
    git_connection = get_token()

    repo = git_connection.get_repo(gh_repo_suffix)
    contrib_file = repo.get_contents(gh_contributors_file)
    return json.loads(contrib_file.decoded_content.decode())


def is_in_identities(discord_id):
    """
    Checks if the discord id is in the list of contributors. These are added by the whitelist command.
    :param discord_id: discord id of user. Using this over name because of name changes.
    :return: True if in list, False if not.
    """
    # TODO Try catch
    identities = get_identities()
    for i in identities:
        if i["details"]["discordId"] == discord_id:
            return True
    return False


def push_identities(identities):
    """
    Pushes the identities to github.
    :param identities: updated json file.
    """
    git_connection = get_token()
    repo = git_connection.get_repo(gh_repo_suffix)
    readme = repo.get_contents(gh_contributors_file)  # change this location after testing phase
    repo.update_file(readme.path, "updated identity", json.dumps(identities, indent=2), readme.sha)


def add_identity(account, type, discord_id, discord_name, github_id, twitter_id):
    """
    Adds a new identity to the json file and pushes it to github.
    :param account: 0L address
    :param type: type of identity:
        0 = contributor: optional fields = 'githubId', 'twitterId', 'discordId', 'discordName', ...
        1 = team: optional fields = 'name', 'description', 'members', ... (not yet implemented)
    :param discord_id: discord id.
    :param discord_name: current discord name
    :param github_id: github username
    :param twitter_id: twitter username
    """
    identities = get_identities()

    details = {}
    if discord_id is not None:
        details["discordId"] = discord_id
    if discord_name is not None:
        details["discordName"] = discord_name
    if twitter_id is not None:
        details["twitterId"] = twitter_id
    if github_id is not None:
        details["githubId"] = github_id

    # TODO: add more details for team type.

    new_identity = {"account": account,
                    "type": type,
                    "details": details
                    }

    identities.append(new_identity)
    push_identities(identities)

if __name__ == "__main__":
    print(get_token())