import os

class Config():
    GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
    CERT_DIR_PATH = os.getenv("CERT_DIR_PATH")
    # karma repo
    GITHUB_KARMA_OWNER = os.getenv("GITHUB_KARMA_OWNER")
    GITHUB_KARMA_REPO = os.getenv("GITHUB_KARMA_REPO")
    GITHUB_KARMA_CERT_FILENAME = os.getenv("GITHUB_KARMA_CERT_FILENAME")
    GITHUB_KARMA_DATA_DIR = os.getenv("GITHUB_KARMA_DATA_DIR")
    GITHUB_KARMA_CONTRIBUTORS_FILENAME = os.getenv("GITHUB_KARMA_CONTRIBUTORS_FILENAME")
    GITHUB_KARMA_PAYMENTS_FILENAME = os.getenv("GITHUB_KARMA_PAYMENTS_FILENAME")
    # additional repos for which issues need to be ingested
    ISSUES_REPO_LIST = os.getenv("ISSUES_REPO_LIST").split(':')
    # general configs
    FORMAT_TIMESTAMP = "%Y-%m-%dT%H:%M:%S"
    FORMAT_TIMESTAMP_TZ = '%Y-%m-%dT%H:%M:%S.%f%z'
    SYNC_INTERVAL = 15
    