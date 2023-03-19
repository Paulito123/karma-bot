from datetime import datetime
from config import Config
from os import popen
from typing import AnyStr, Dict
from model import OnboardLog
from re import search
from asyncio import AbstractEventLoop, wait



async def onboard_account_async(account_auth: AnyStr) -> Dict:
    """
    Onboard a given account.
    """
    try:
        if not search('^([A-Fa-f0-9]{64})$', account_auth):
            raise Exception('Not a valid authentication address.')

        command_string = f"{Config.ONBOARD_FILEPATH} {account_auth} \"{Config.MNEM}\""

        with popen(command_string,'w') as f:
            bingo = False
            for line in f.readlines():
                if search(f'([Success: Account created for authkey: {account_auth}])', line):
                    bingo = True
                    break
            if not bingo:
                raise Exception('Transaction failed.')
        
        return {"status": "success", "message": f"Success: Account created for authkey: {account_auth}"}

    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")
        return {"status": "failed", "message": f"{e}"}


async def handle_onboard_requests(account_auth: AnyStr):
    """ 
    Wrapper to handle the outcome of the onboard request.
    """
    res = await onboard_account_async(account_auth)
    if res["status"] == "success":
        OnboardLog.close_onboard_request(account_auth)
    print(res["message"])


def run_onboard_tasks(loop: AbstractEventLoop):
    """
    Loop through all the open onboard candidates.
    """
    # Get open onboard candidates
    onboard_candidates = OnboardLog.get_onboard_candidates()

    # Loop through all the open onboard candidates
    if len(onboard_candidates) > 0:

        # Create tasks
        tasks = [handle_onboard_requests(f"{single_candidate.address}") for single_candidate in onboard_candidates]

        # Loop through all the tasks
        loop.run_until_complete(wait(tasks))
