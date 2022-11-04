# Fetching block
do_fetch = False
# With 'False' will only append new Issue files.
# If smth was changed for issues from last run - better to set to 'True'
clear_previous_fetch = False

# Parsing block
do_parse = True
# With 'False' will only parse not parsed issues.
# If smth was changed in parsing logic - better to set to 'True'
clear_previous_parse = False

# Dirs
# Set prod=False, do_fetch=False to experiment on test data
prod = True
issues_suffix = "prod" if prod else "test"
issues_dir = "issues/{}/parsed".format(issues_suffix)
issues_rest = "issues/{}/rest".format(issues_suffix)
issues_tmp = "issues/{}/tmp".format(issues_suffix)
issues_result = "issues/{}/result/people_sps.json".format(issues_suffix)

# Statuses. Need to clean up
statuses_backlog_dev = ["To Do"]
statuses_inprogress_dev = ["In Progress", "Code Review"]
statuses_backlog_test = ["Ready for Test"]
statuses_inprogress_test = ["In Test"]
statuses_deploy = ["Tested", "Finish Feature", "Ready for Release", "UAT", "To deploy to Prod"]
