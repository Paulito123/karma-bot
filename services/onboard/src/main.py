from time import sleep
from datetime import datetime, timedelta
from asyncio import get_event_loop

from toolz import run_onboard_tasks
from config import Config


if __name__ == "__main__":
    last_trigger_hour = datetime.now() - timedelta(hours=1.01)
    last_trigger_day = datetime.now() - timedelta(days=1.01)
    loop = get_event_loop()
    while True:
        # sync start time
        start_cycle = datetime.now()

        # TRIGGET EVERY CYCLE
        run_onboard_tasks(loop)

        # TRIGGER EVERY HOUR
        if last_trigger_hour <= datetime.now() - timedelta(hours=1):
            ...
            last_trigger_hour = start_cycle
        
        # TRIGGER EVERY DAY
        if last_trigger_day <= datetime.now() - timedelta(days=1):
            ...
            last_trigger_day = start_cycle
        
        # sync end time
        end_cycle = datetime.now()

        # calculate sleepy time
        secs_between = int((end_cycle - start_cycle).total_seconds())
        if secs_between < Config.SYNC_INTERVAL:
            sleepytime = Config.SYNC_INTERVAL - secs_between
            print(f"[{datetime.now()}]:INFO:ZzZzZz...")
            sleep(sleepytime)
