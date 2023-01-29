from datetime import datetime
from config import Config
# from model import Contributor
from os import popen
from typing import AnyStr
from re import search


def onboard_account(account_auth: AnyStr) -> AnyStr:
    try:
        if not search('^([A-Fa-f0-9]{64})$', account_auth):
            raise Exception('Not a valid authentication address.')

        command_string = f"{Config.ONBOARD_FILEPATH} {account_auth} \"{Config.MNEM}\""
        stdout = popen(command_string,'w')
        chain_message = stdout
        stdout.close()
        return f'{{"status": "success", "message": "{chain_message}"}}'

    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")
        return f'{{"status": "failed", "message": "{e}"}}'
