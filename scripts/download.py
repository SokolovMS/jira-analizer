import logging

from jira import JIRA

import config
import secrets
from scripts import files


def fetch_issues():
    logging.info("\n----- Started downloading Jira issues -----")

    jira = JIRA(secrets.jira_url, auth=(secrets.jira_username, secrets.jira_password))

    size = 100
    initial = 0

    added = 0
    skipped = 0

    ids = []
    while True:
        start = initial * size
        issues = jira.search_issues(secrets.jira_query_str, start, size, expand="changelog")
        if len(issues) == 0:
            break
        initial += 1
        for issue in issues:
            issue_id = issue.key
            issue_json = issue.raw

            if files.file_exists("{}/{}.json".format(config.issues_rest, issue_id)):
                skipped += 1
                continue

            files.json_dump("{}/{}.json".format(config.issues_rest, issue_id), issue_json)
            added += 1

    logging.info("----- Fetched issues: New {}, Skipped {} -----\n".format(added, skipped))

    return ids
