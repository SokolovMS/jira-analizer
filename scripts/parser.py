import logging
from collections import defaultdict
from functools import cmp_to_key

import config
from scripts import files
from scripts.dates import JiraDatesDecoder


def parse_everything():
    logging.info("----- Parse Jira issues: Started -----")

    added = 0
    skipped = 0
    for input_file in files.file_list(config.issues_rest):
        skipped += 1
        issue_id = input_file.stem
        output_file_path = "{}/{}.json".format(config.issues_dir, issue_id)
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
    result['summary'] = {
        "analysis": {
            "sp": None,
            "start": None,
            "end": None,
            "assignee": None
        },
        "dev": {
            "sp": None,
            "start": None,
            "end": None,
            "assignee": None
        },
        "qa": {
            "sp": None,
            "start": None,
            "end": None,
            "assignee": None
        }
    }

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

            if item['field'] == "Story Points":
                result['summary']["dev"]["sp"] = item['toString']

        if status_item:
            changelog.append(status_item)

        if assignee_item:
            changelog.append(assignee_item)

    changelog = sorted(changelog, key=cmp_to_key(custom_compare))
    changelog.insert(0, {
        "field": "assignee",
        "fromString": None,
        "toString": next((x["fromString"] for x in changelog if x["field"] == "assignee"), None),
        "date": next((x["date"] for x in changelog if x["date"]), None)
    })

    # TODO: ordered_changelog = sorted(data.items(), key=lambda x: datetime.strptime(x[0], '%d-%m-%Y'), reverse=True)
    time_in_status = defaultdict(dict)
    prev_status = None
    assignee = None
    for item in changelog:
        if item['field'] == "assignee":
            assignee = item['toString']
            continue

        if not prev_status:
            prev_status = item['toString']
            prev_date = item['date']
            continue

        date_diff = item['date'] - prev_date
        if prev_status in time_in_status:
            time_in_status[prev_status]["dt"] += date_diff
            time_in_status[prev_status]["assignee"].add(assignee)
        else:
            time_in_status[prev_status]["dt"] = date_diff
            time_in_status[prev_status]["assignee"] = {assignee}

        update_dev_parts(result, item)

        prev_status = item['toString']
        prev_date = item['date']

    for key in time_in_status:
        ass_set = time_in_status[key]["assignee"]
        ass_set.discard(None)
        time_in_status[key]["assignee"] = ass_set
        if len(time_in_status[key]["assignee"]) == 0:
            time_in_status[key]["assignee"] = "None"
        if len(time_in_status[key]["assignee"]) == 1:
            time_in_status[key]["assignee"] = time_in_status[key]["assignee"].pop()

    result['time_in_status'] = time_in_status

    if time_in_status["In Progress"] and time_in_status["In Progress"]["assignee"]:
        result['summary']['dev']["assignee"] = time_in_status["In Progress"]["assignee"]

    return result


def custom_compare(changelog_item1, changelog_item2):
    if changelog_item1['date'] < changelog_item2['date']:
        return -1
    elif changelog_item1['date'] > changelog_item2['date']:
        return 1

    if changelog_item1['field'] == 'assignee':
        return 1
    elif changelog_item2['field'] == 'assignee':
        return -1

    return 0


def update_dev_parts(result, item):
    if item['field'] != "status":
        return

    if item['toString'] in config.statuses_inprogress_dev:
        if not result['summary']['dev']['start']:
            result['summary']['dev']['start'] = item['date']
        else:
            result['summary']['dev']['start'] = min(result['summary']['dev']['start'], item['date'])

    if item['fromString'] in config.statuses_inprogress_dev:
        if not result['summary']['dev']['end']:
            result['summary']['dev']['end'] = item['date']
        else:
            result['summary']['dev']['end'] = max(result['summary']['dev']['end'], item['date'])
