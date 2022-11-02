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

## Before push
```
python3 -m pipreqs.pipreqs . --force
```