from chores import sync_contributors
from time import sleep
from config import Config


if __name__ == "__main__":
    while True:
        sync_contributors()
        sleep(Config.SYNC_INTERVAL)
