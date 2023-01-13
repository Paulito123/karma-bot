from chores import sync_contributors, sync_issues
from time import sleep
from config import Config
from datetime import datetime, timedelta


if __name__ == "__main__":
    last_trigger_hour = datetime.now() - timedelta(hours=1.01)
    last_trigger_day = datetime.now() - timedelta(days=1.01)
    while True:
        # sync start time
        start_cycle = datetime.now()

        # TRIGGET EVERY CYCLE
        sync_contributors()

        # TRIGGER EVERY HOUR
        if last_trigger_hour <= datetime.now() - timedelta(hours=1):
            ...
        
        # TRIGGER EVERY DAY
        if last_trigger_day <= datetime.now() - timedelta(days=1):
            # sync_issues()
            ...
        
        # sync end time
        end_cycle = datetime.now()

        # calculate sleepy time
        secs_between = int((end_cycle - start_cycle).total_seconds())
        if secs_between < Config.SYNC_INTERVAL:
            sleepytime = Config.SYNC_INTERVAL - secs_between
            sleep(sleepytime)
