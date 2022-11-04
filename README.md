# jira-analizer
## Before you begin
```
# Install python3
https://www.python.org/downloads/

# To disable accidental committing of your secrets
git update-index --skip-worktree secrets.py

# Download required python libs
pip3 install -r requirements.txt
```

## Working with lib
```
# Fill in secrets.py
Example for param: jira_query_str = "project=YOUR_PROJECT_NAME"

# Check config.py
Use your eyes and logic

# Run from CLI / Pycharm
python3 main.py
```

## Before push
```
python3 -m pipreqs.pipreqs . --force
```