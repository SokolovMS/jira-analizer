# Fetching block
do_fetch = False
# With 'False' will only append new Issue files.
# If smth was changed for issues from last run - better to set to 'True'
clear_previous_fetch = False

# Parsing block
do_parse = False
# With 'False' will only parse not parsed issues.
# If smth was changed in parsing logic - better to set to 'True'
clear_previous_parse = False

# Dirs
# Set prod=False, do_fetch=False to experiment on test data
prod = True
issues_suffix = "prod" if prod else "test"
issues_rest = "issues/{}/rest".format(issues_suffix)
issues_rest_final = "{}/final".format(issues_rest)
issues_rest_not_final = "{}/notfinal".format(issues_rest)
issues_parsed = "issues/{}/parsed".format(issues_suffix)
issues_result = "issues/" + issues_suffix + "/result/people_sps_{}.json"

# Statuses. Need to clean up
jira_status_final = ["Released", "Cancelled", "Done", "Closed", "Deleted"]
jira_tracked_statuses = {
    "Analysis": {
        "jira_estimation_field": "Analysis Estimation"
    },
    "In Progress": {
        "jira_estimation_field": "customfield_10022"
    },
    "In Test": {
        "jira_estimation_field": "customfield_21102"
    }
}
statuses_backlog_dev = ["To Do"]
statuses_inprogress_dev = ["In Progress", "Code Review"]
statuses_backlog_test = ["Ready for Test"]
statuses_inprogress_test = ["In Test"]
statuses_deploy = ["Tested", "Finish Feature", "Ready for Release", "UAT", "To deploy to Prod"]
