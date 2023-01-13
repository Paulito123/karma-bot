from github_util import (
    get_identities, 
    push_identities,
    get_issues
)
from datetime import datetime
from config import Config
from model import Contributor, GithubIssue

def sync_contributors() -> None:
    try:
        # get file from github
        contributors = get_identities()
        
        file_last_ts = datetime.strptime(contributors['timestamp_last_update'], Config.FORMAT_TIMESTAMP_TZ)
        file_rec_count = len(contributors['data'])
        
        # get last update date from db
        result = Contributor.get_update_metrics()
        
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
            if Contributor.upload_contributors_json(contributors):
                # making sure the update timestamp is also pushed back to the file
                identities = Contributor.get_contributors(Contributor)
                push_identities(identities)

    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")


def sync_issues() -> None:
    try:
        # itertate repos from which issues must be ingested
        for repo in Config.ISSUES_REPO_LIST:
            # get issues for a given repo
            issues = get_issues(repository=repo, state="all")
            GithubIssue.upload_gh_response(issues)
    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")
