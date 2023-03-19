import os

# from dotenv import load_dotenv

# load_dotenv('/home/user/projects/karma-bot/services/onboard/.env.dev')

class Config():
    # general configs
    FORMAT_TIMESTAMP = "%Y-%m-%dT%H:%M:%S"
    FORMAT_TIMESTAMP_TZ = '%Y-%m-%dT%H:%M:%S.%f%z'
    SYNC_INTERVAL = 15

    MNEM = os.environ.get('MNEM')
    ONBOARD_FILEPATH = os.environ.get('ONBOARD_FILEPATH')
    DATABASE_URL = os.environ.get('DATABASE_URL')

if __name__ == '__main__':
    print(Config.DATABASE_URL)