# Fetching block
do_fetch = True
# With 'False' will only append new Issue files.
# If smth was changed for issues from last run - better to set to 'True'
clear_previous_fetch = False

# Parsing block
do_parse = True
# With 'False' will only parse not parsed issues.
# If smth was changed in parsing logic - better to set to 'True'
clear_previous_parse = False

# Analysis block
# 'days_back' will analyze only tasks for last days (Doesn't affect fetching filter. Everything will be downloaded)
days_back = 90

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
    "In Progress": {
        "jira_estimation_field": "customfield_10022"
    },
    "In Test": {
        "jira_estimation_field": "customfield_21102"
    }
}
