import logging
from collections import defaultdict
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


def compute_time_in_status(changelog):
    time_in_status = defaultdict(dict)
    prev_status = None
    prev_transition_date = None
    assignee = None
    for item in changelog:
        # Working with 'assignee' changelog item
        if item['field'] == "assignee":
            assignee = item['toString']
            update_assignee(time_in_status, prev_status, assignee)
            continue

        # Working with 'status' changelog item
        prev_status = item['fromString']
        curr_status = item['toString']
        curr_transition_date = item['date']
        date_diff = curr_transition_date - prev_transition_date if prev_transition_date else None

        update_dt(time_in_status, prev_status, date_diff)
        update_end(time_in_status, prev_status, curr_transition_date)

        update_start(time_in_status, curr_status, curr_transition_date)
        update_dt(time_in_status, curr_status, date_diff)
        update_assignee(time_in_status, curr_status, assignee)

        prev_status = curr_status
        prev_transition_date = curr_transition_date

    for key in time_in_status:
        ass_set = time_in_status[key].get("assignee", set())
        ass_set.discard(None)
        time_in_status[key]["assignee"] = ass_set
        if len(time_in_status[key]["assignee"]) == 0:
            time_in_status[key]["assignee"] = "None"
        elif len(time_in_status[key]["assignee"]) == 1:
            time_in_status[key]["assignee"] = time_in_status[key]["assignee"].pop()
        # else:
        #     time_in_status[key]["assignee"] = time_in_status[key]["assignee"]
    return time_in_status


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
    # changelog.insert(0, {
    #     "field": "assignee",
    #     "fromString": None,
    #     "toString": next((x["fromString"] for x in changelog if x["field"] == "assignee"), None),
    #     "date": next((x["date"] for x in changelog if x["date"]), None)
    # })
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
    current.add(assignee)
    time_in_status[status]["assignee"] = current


def custom_compare(changelog_item1, changelog_item2):
    if changelog_item1['date'] < changelog_item2['date']:
        return -1
    elif changelog_item1['date'] > changelog_item2['date']:
        return 1

    if changelog_item1['field'] == 'assignee':
        return -1
    elif changelog_item2['field'] == 'assignee':
        return 1

    return 0


def add_estimation_info(result, input_json):
    for status in config.jira_tracked_statuses:
        jira_estimation_field = config.jira_tracked_statuses[status]['jira_estimation_field']
        result['time_in_status'].get(status, {})["estimation"] = input_json['fields'].get(jira_estimation_field, None)
