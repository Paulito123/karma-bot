from github_util import get_identities, push_identities
from datetime import datetime
from config import Config
from model import Contributor

def sync_contributors():
    try:
        # get file from github
        contributors = get_identities()
        
        file_last_ts = datetime.strptime(contributors['timestamp_last_update'], Config.FORMAT_TIMESTAMP_TZ)
        file_rec_count = len(contributors['data'])
        
        # get last update date from db
        result = Contributor.get_update_metrics()
        print(result)
        db_last_ts = result[0]
        db_rec_count = result[1]
        
        if db_rec_count > 0:
            # compare timestamps
            if db_last_ts > file_last_ts and db_rec_count >= file_rec_count:
                # If we arrive here, we assume the database has more recent data
                # than the file on github. We therefore push the database data to
                # the github file.
                # update file
                identities = Contributor.get_contributors(Contributor)
                push_identities(identities)
        else:
            # If we arrive here, we assume the database is empty so we need to
            # push the file data to the database.
            # upload file to db
            print(contributors)
            if Contributor.upload_contributors_json(contributors):
                print(2)
                # making sure the update timestamp is also pushed back to the file
                identities = Contributor.get_contributors(Contributor)
                print(identities)
                push_identities(identities)

    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")
    