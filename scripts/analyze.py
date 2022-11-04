import copy
import datetime
import logging
from collections import defaultdict
from datetime import datetime, timedelta

import config
from scripts import files
from scripts.dates import tz, OwnDatesDecoder


def gather_stats(days_back=config.days_back, author=None):
    start_date = datetime.now(tz=tz()) - timedelta(days=days_back)
    gather_stats_main(start_date, author)


def gather_stats_main(start_date=None, author=None):
    logging.info("----- Gather stats: Started for start date {} and author {} -----".format(start_date, author))

    issues = get_issues()

    for status in config.jira_tracked_statuses:
        gather_stats_for_status(issues, status, start_date)

    logging.info("----- Gather stats: Done -----")


def gather_stats_for_status(issues, status, start_date=None):
    issues_list = list(filter(lambda i: end_is_set_and_after_search_date(i, status, start_date), issues))
    issues_list = copy.deepcopy(issues_list)

    # If task was started before start date - count only part of Estimation
    for issue in issues_list:
        # issue['time_in_status_1'] = issue['time_in_status']
        tis = issue['time_in_status'][status]
        issue['time_in_status'] = {status: tis}

        if start(issue, status) < start_date:
            curr_est = estimation(issue, status)

            dt_all = end(issue, status) - start(issue, status)
            dt_required = end(issue, status) - start_date
            new_est = curr_est * dt_required / dt_all

            logging.info("Changing SP for {} from {} to {}".format(issue['key'], curr_est, new_est))
            issue['time_in_status'][status]['estimation'] = new_est
            issue['time_in_status'][status]['start'] = start_date

    issues_list.sort(key=lambda i: start(i, status))

    dev_issues_dict = defaultdict(list)
    for issue in issues_list:
        assignee = issue['time_in_status'][status]['assignee']
        current = {
            'estimation': estimation(issue, status),
            'start': start(issue, status),
            'end': end(issue, status),
            'issues_count': 1,
            'issues': [issue]
        }

        if assignee not in dev_issues_dict:
            dev_issues_dict[assignee] = current
        else:
            existing = dev_issues_dict[assignee]
            existing['estimation'] += current['estimation']
            existing['start'] = min(current['start'], existing['start'])
            existing['end'] = max(current['end'], existing['end'])
            existing['issues_count'] += current['issues_count']
            existing['issues'].append(issue)
            dev_issues_dict[assignee] = existing

    files.json_dump(config.issues_result.format(status.replace(" ", "_")), dev_issues_dict)


def end_is_set_and_after_search_date(issue, status, start_date):
    return end(issue, status) and end(issue, status) >= start_date


def end(issue, status):
    return issue['time_in_status'].get(status, {}).get('end', None)


def start(issue, status):
    return issue['time_in_status'][status]['start']


def estimation(issue, status):
    result = issue['time_in_status'][status].get("estimation", 0.0)
    return result if result else 0.0


def get_issues():
    issues = list()
    for input_file in files.file_list(config.issues_parsed):
        input_json = files.safe_read_as_json(input_file, OwnDatesDecoder)
        issues.append(input_json)

    return issues
