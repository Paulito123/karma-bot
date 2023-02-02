from datetime import datetime
from config import Config
# from model import OnboardLog
from os import popen
from typing import AnyStr, Dict
from re import search


def onboard_account(account_auth: AnyStr) -> Dict:
    try:
        if not search('^([A-Fa-f0-9]{64})$', account_auth):
            raise Exception('Not a valid authentication address.')

        command_string = f"{Config.ONBOARD_FILEPATH} {account_auth} \"{Config.MNEM}\""
        stdout = popen(command_string,'w')
        chain_message = stdout
        stdout.close()
        return {"status": "success", "message": f"{chain_message}"}

    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")
        return {"status": "failed", "message": f"{e}"}


async def onboard_account_async(account_auth: AnyStr) -> Dict:
    try:
        if not search('^([A-Fa-f0-9]{64})$', account_auth):
            raise Exception('Not a valid authentication address.')

        command_string = f"{Config.ONBOARD_FILEPATH} {account_auth} \"{Config.MNEM}\""
        stdout = popen(command_string,'w')
        #TODO: capture stdout into str or list for further evaluation...
        chain_message = stdout
        stdout.close()
        
        if not search(f'([Success: Account created for authkey: {account_auth}])', chain_message):
            raise Exception('Transaction failed.')

        return {"status": "success", "message": f"{chain_message}"}

    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")
        return {"status": "failed", "message": f"{e}"}
