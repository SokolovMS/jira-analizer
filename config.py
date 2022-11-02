statuses_backlog_dev = ["To Do"]
statuses_inprogress_dev = ["In Progress", "Code Review"]
statuses_backlog_test = ["Ready for Test"]
statuses_inprogress_test = ["In Test"]
statuses_deploy = ["Tested", "Finish Feature", "Ready for Release", "UAT", "To deploy to Prod"]

prod = True
issues_suffix = "prod" if prod else "test"
issues_dir = "issues/{}/parsed".format(issues_suffix)
issues_rest = "issues/{}/rest".format(issues_suffix)
issues_tmp = "issues/{}/tmp".format(issues_suffix)
issues_result = "issues/{}/result/people_sps.json".format(issues_suffix)
