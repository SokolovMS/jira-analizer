import logging
from collections import defaultdict
from datetime import timedelta
from functools import cmp_to_key
from itertools import chain

import config
from scripts import files
from scripts.dates import JiraDatesDecoder


def parse_everything():
    logging.info("----- Parse Jira issues: Started -----")

    added = 0
    skipped = 0
    for input_file in chain(files.file_list(config.issues_rest_final), files.file_list(config.issues_rest_not_final)):
        skipped += 1
        issue_id = input_file.stem
        output_file_path = "{}/{}.json".format(config.issues_parsed, issue_id)
        if not files.file_exists(output_file_path):
            input_json = files.safe_read_as_json(input_file, decoder=JiraDatesDecoder)
            parsed = parse(input_json)
            if parsed:
                files.json_dump(output_file_path, parsed)
                added += 1
                skipped -= 1

    logging.info("----- Parse Jira issues: Done = New {}, Skipped {} -----".format(added, skipped))


def parse(input_json):
    result = dict()

    result['key'] = input_json['key']
    result['status'] = input_json['fields']['status']['name']
    result['resolutiondate'] = input_json['fields']['resolutiondate']
    result['name'] = input_json['fields']['summary']

    changelog = get_sorted_changelog(input_json)
    time_in_status = compute_time_in_status(changelog)
    result['time_in_status'] = time_in_status

    add_estimation_info(result, input_json)

    return result


def how_long_was_assigned(time_in_status, prev_status, assignee, assignee_transition_date):
    if not prev_status or not time_in_status[prev_status]:
        return

    prev_end = time_in_status[prev_status].get("end", assignee_transition_date)

    if 'assignees' not in time_in_status[prev_status]:
        time_in_status[prev_status]['assignees'] = {}
    if assignee not in time_in_status[prev_status]['assignees']:
        time_in_status[prev_status]['assignees'][assignee] = timedelta(days=0)

    time_in_status[prev_status]['assignees'][assignee] += (assignee_transition_date - prev_end)
    time_in_status[prev_status]['end'] = assignee_transition_date


def compute_time_in_status(changelog):
    time_in_status = defaultdict(dict)
    prev_status = None
    prev_transition_date = None
    assignee = None
    for item in changelog:
        if not config.prod:
            logging.debug("Processing item: {}".format(item))

        # Working with 'assignee' changelog item
        if item['field'] == "assignee":
            assignee = item['toString']
            assignee_transition_date = item['date']
            how_long_was_assigned(time_in_status, prev_status, assignee, assignee_transition_date)
            continue

        # Working with 'status' changelog item
        prev_status = item['fromString']
        curr_status = item['toString']
        curr_transition_date = item['date']
        date_diff = curr_transition_date - prev_transition_date if prev_transition_date else None

        how_long_was_assigned(time_in_status, prev_status, assignee, curr_transition_date)
        update_dt(time_in_status, prev_status, date_diff)
        update_end(time_in_status, prev_status, curr_transition_date)

        update_start(time_in_status, curr_status, curr_transition_date)
        update_end(time_in_status, curr_status, curr_transition_date)

        prev_status = curr_status
        prev_transition_date = curr_transition_date

    for status in time_in_status:
        time_in_status[status]["assignee"] = get_longest_assignee(time_in_status, status)

    return time_in_status


def get_longest_assignee(time_in_status, status):
    if "assignees" not in time_in_status[status]:
        return None

    assignees = time_in_status[status]["assignees"]
    return max(assignees, key=assignees.get)


def get_sorted_changelog(input_json):
    changelog = []
    for history in input_json['changelog']['histories']:
        status_item = None
        assignee_item = None

        for item in history['items']:
            if item['field'] == "status":
                status_item = {
                    "field": item['field'],
                    "fromString": item['fromString'],
                    "toString": item['toString'],
                    "date": history['created']
                }

            if item['field'] == "assignee":
                assignee_item = {
                    "field": item['field'],
                    "fromString": item['fromString'],
                    "toString": item['toString'],
                    "date": history['created']
                }

        if status_item:
            changelog.append(status_item)

        if assignee_item:
            changelog.append(assignee_item)
    changelog = sorted(changelog, key=cmp_to_key(custom_compare))
    return changelog


def update_dt(time_in_status, status, dt):
    current_dt = time_in_status.get(status, {}).get("dt", None)
    if current_dt:
        time_in_status[status]["dt"] += dt
    else:
        time_in_status[status]["dt"] = dt


def update_start(time_in_status, status, date):
    current = time_in_status.get(status, {}).get("start", None)
    if current:
        time_in_status[status]["start"] = min(date, current)
    else:
        time_in_status[status]["start"] = date


def update_end(time_in_status, status, date):
    current = time_in_status.get(status, {}).get("end", None)
    if current:
        time_in_status[status]["end"] = max(date, current)
    else:
        time_in_status[status]["end"] = date


def update_assignee(time_in_status, status, assignee):
    if not status:
        return

    current = time_in_status.get(status, {}).get("assignee", set())

    if not config.prod:
        if status == "In Progress":
            logging.debug("Updating assignee. Before: {}".format(current))

    current.add(assignee)
    time_in_status[status]["assignee"] = current

    if not config.prod:
        if status == "In Progress":
            logging.debug("Updating assignee. After: {}".format(time_in_status[status]["assignee"]))


def custom_compare(changelog_item1, changelog_item2):
    if changelog_item1['date'] < changelog_item2['date']:
        return -1
    elif changelog_item1['date'] > changelog_item2['date']:
        return 1

    # Assignee changes after status changes
    if changelog_item1['field'] == 'assignee':
        return 1
    elif changelog_item2['field'] == 'assignee':
        return -1

    return 0


def add_estimation_info(result, input_json):
    for status in config.jira_tracked_statuses:
        jira_estimation_field = config.jira_tracked_statuses[status]['jira_estimation_field']
        result['time_in_status'].get(status, {})["estimation"] = input_json['fields'].get(jira_estimation_field, None)
