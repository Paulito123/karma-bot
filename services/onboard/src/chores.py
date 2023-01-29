from datetime import datetime
from config import Config
from model import Contributor #, GithubIssue


def sync_contributors() -> None:
    try:
        # get file from github
        contributors = get_identities()

        if not contributors:
            raise Exception('Initiate contributors file!')
        
        file_last_ts = datetime.strptime(contributors['timestamp_last_update'], Config.FORMAT_TIMESTAMP_TZ)
        file_rec_count = len(contributors['data'])

        # get last update date from db
        result = Contributor.get_update_metrics()

        if not result:
            raise Exception('Cannot connect to database or database model not initialized!')
        
        if not result[0]:
            db_last_ts = datetime.strptime("2000-01-01T00:00:00.000000+0000", Config.FORMAT_TIMESTAMP_TZ)
        else:
            db_last_ts = result[0]
        db_rec_count = result[1]

        if db_rec_count == 0 and file_rec_count == 0:
            # Do nothing
            ...
        elif db_rec_count > 0:
            # compare timestamps
            if db_last_ts > file_last_ts and db_rec_count >= file_rec_count:
                # If we arrive here, we assume the database has more recent data
                # than the file on github. We therefore push the database to
                # the github file.
                identities = Contributor.get_contributors(Contributor)
                push_identities(identities)
        elif db_rec_count == 0 and file_rec_count > 0:
            # if we arrive here, the db must be initialized
            if Contributor.upload_contributors_json(contributors):
                # making sure the update timestamp is also pushed back to the file
                identities = Contributor.get_contributors(Contributor)
                push_identities(identities)
    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")

