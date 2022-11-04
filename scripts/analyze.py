import datetime
import logging
from collections import defaultdict
from datetime import datetime, timedelta

import config
from scripts import files
from scripts.dates import tz, OwnDatesDecoder


def gather_stats(days_back=None, author=None):
    start_date = datetime.now(tz=tz()) - timedelta(days=days_back)
    gather_stats_main(start_date, author)


def gather_stats_main(start_date=None, author=None):
    logging.info("----- Gather stats: Started for start date {} and author {} -----".format(start_date, author))

    issues = get_issues()
    gather_dev_stats(issues, start_date)

    if start_date:
        issues = list(filter(lambda issue: issue["resolutiondate"] is None or issue["resolutiondate"] >= start_date, issues))

    # if author:
    #     issues = list(filter(lambda issue: issue["resolutiondate"] is None or issue["resolutiondate"] >= start_date, issues))

    # short_issues = list(map(lambda issue: (issue["key"], issue["resolutiondate"]), issues))
    # logging.info("Found {} issues: {}".format(len(short_issues), short_issues))

    # In progress
    # sp_status_time = analyze_dev(issues)

    # print(sp_status_time)
    logging.info("----- Gather stats: Done -----")


def gather_dev_stats(issues, start_date=None):
    # dev_issues_list = list(filter(lambda issue: issue['resolutiondate'] >= start_date, issues))
    dev_issues_list = list(filter(lambda issue: issue['summary']['dev']['end'] >= start_date, issues))

    # Если задачу начали делать задолго раньше, учтём только часть задачи, попавшую во временной интервал
    for issue in dev_issues_list:
        if issue['summary']['dev']['start'] < start_date:
            curr_sp = issue['summary']['dev']['sp']
            if not curr_sp or curr_sp == 0:
                issue['summary']['dev']['start'] = start_date
                continue

            dt_all = issue['summary']['dev']['end'] - issue['summary']['dev']['start']
            dt_required = issue['summary']['dev']['end'] - start_date
            sp_new = curr_sp * dt_required / dt_all

            logging.info("Changing SP for {} from {} to {}".format(issue['key'], curr_sp, sp_new))
            issue['summary']['dev']['sp'] = sp_new
            issue['summary']['dev']['start'] = start_date

    dev_issues_list.sort(key=lambda issue: issue['summary']['dev']['start'])
    # logging.info("Found {} dev issues: {}".format(len(dev_issues_list), dev_issues_list))

    dev_issues_dict = defaultdict(list)
    for issue in dev_issues_list:
        assignee = issue['summary']['dev']['assignee']
        current = {
            'sp': issue['summary']['dev']['sp'],
            'start': issue['summary']['dev']['start'],
            'end': issue['summary']['dev']['end'],
            'issues_count': 1,
            'issues': [issue]
        }

        if assignee not in dev_issues_dict:
            dev_issues_dict[assignee] = current
        else:
            existing = dev_issues_dict[assignee]
            existing['sp'] += current['sp']
            existing['start'] = min(current['start'], existing['start'])
            existing['end'] = max(current['end'], existing['end'])
            existing['issues_count'] += current['issues_count']
            existing['issues'].append(issue)
            dev_issues_dict[assignee] = existing

    # logging.info("Found {} dev issues: {}".format(len(dev_issues_dict), dev_issues_dict))
    files.json_dump(config.issues_result, dev_issues_dict)


def get_issues():
    issues = list()
    for input_file in files.file_list(config.issues_parsed):
        input_json = files.safe_read_as_json(input_file, OwnDatesDecoder)
        input_json["resolutiondate"] = input_json["resolutiondate"]

        # dev
        if input_json['summary']['dev']['start']:
            input_json['summary']['dev']['start'] = input_json['summary']['dev']['start']
        else:
            input_json['summary']['dev']['start'] = datetime(year=2007, month=1, day=1, tzinfo=tz())

        if input_json['summary']['dev']['end']:
            input_json['summary']['dev']['end'] = input_json['summary']['dev']['end']
        else:
            input_json['summary']['dev']['end'] = datetime(year=2007, month=1, day=1, tzinfo=tz())

        if input_json['summary']['dev']['sp']:
            input_json['summary']['dev']['sp'] = float(input_json['summary']['dev']['sp'])
        else:
            input_json['summary']['dev']['sp'] = 0.0

        issues.append(input_json)

    return issues
