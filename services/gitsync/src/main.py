from chores import sync_contributors
from time import sleep
# from github_util import get_token
from config import Config
import json
from github import Github, GithubIntegration, enable_console_debug_logging


if __name__ == "__main__":
    counter = 0
    while True:
        sync_contributors()

        sleep(120)
