from datetime import datetime
from config import Config
from model import OnboardLog
from os import popen
from typing import AnyStr
from re import search
from toolz import onboard_account, onboard_account_async
import asyncio
from time import sleep


async def handle_onboard_requests(account_auth: AnyStr):
    res = await onboard_account_async(account_auth)
    if res["status"] == "success":
        print("success!")
        OnboardLog.close_onboard_request(account_auth)
    else:
        ...


def run_onboard_tasks(loop: asyncio.AbstractEventLoop):
    onboard_candidates = OnboardLog.get_onboard_candidates()
    if len(onboard_candidates) > 0:
        tasks = [handle_onboard_requests(f"{single_candidate.address}") for single_candidate in onboard_candidates]
        loop.run_until_complete(asyncio.wait(tasks))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        print("runnin")
        run_onboard_tasks(loop)
        print("sleepin")
        sleep(60)
