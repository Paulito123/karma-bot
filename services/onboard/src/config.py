import os


class Config():
    # general configs
    FORMAT_TIMESTAMP = "%Y-%m-%dT%H:%M:%S"
    FORMAT_TIMESTAMP_TZ = '%Y-%m-%dT%H:%M:%S.%f%z'
    SYNC_INTERVAL = 15

    MNEM = os.environ.get('MNEM')
    ONBOARD_FILEPATH = os.environ.get('ONBOARD_FILEPATH')
    