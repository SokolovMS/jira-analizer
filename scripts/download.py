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
    in_final_status = 0
    not_in_final_status = 0

    statuses = set()
    while True:
        start = initial * size
        issues = jira.search_issues(secrets.jira_query_str, start, size, expand="changelog")
        if len(issues) == 0:
            break
        initial += 1
        for issue in issues:
            issue_id = issue.key
            issue_json = issue.raw
            issue_status = issue_json['fields']['status']['name']
            statuses.add(issue_status)

            if files.file_exists("{}/{}.json".format(config.issues_rest_final, issue_id)):
                skipped += 1
                continue

            if issue_status in config.jira_status_final:
                base_dir = config.issues_rest_final
                in_final_status += 1
            else:
                base_dir = config.issues_rest_not_final
                not_in_final_status += 1
            files.json_dump("{}/{}.json".format(base_dir, issue_id), issue_json)
            added += 1

    logging.info("----- Fetched issues: New {}, Skipped {} -----\n".format(added, skipped))
    logging.info("----- Saved issues: In final status {}, Not {} -----\n".format(in_final_status, not_in_final_status))
    logging.info("Found statuses: {}".format(statuses))
    logging.info("Known final statuses: {}".format(config.jira_status_final))

    return added
