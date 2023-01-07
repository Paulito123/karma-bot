from connect import engine, session
from github_util import get_token, get_identities
from datetime import datetime

def sync_contributors():
    try:
        ids = get_identities()
        print(ids)
    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")
    