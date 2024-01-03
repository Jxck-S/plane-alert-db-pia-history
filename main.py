#From GitPython pip Package
import git
import subprocess

# Define the path to the file you want to track
file_path = "plane-alert-pia.csv"

# Define the repository URL and target directory
repo_url = 'https://github.com/sdr-enthusiasts/plane-alert-db.git'
repo_path = 'plane-alert-db.git'

# Run the git clone command with --bare option
subprocess.run(['git', 'clone', '--bare', repo_url, repo_path], check=True)
# Create a Repo object
repo = git.Repo(repo_path)

# Iterate through all the commits in the repository
record_history = {}
for commit in reversed(list(repo.iter_commits(paths=file_path))):
    # Use Git to show the differences for the file in the commit
    commit_datetime = commit.committed_datetime
    try:
        commit_diff = repo.git.diff("-U0", f"{commit.hexsha}^..{commit.hexsha}", "--", file_path)
        # Split the changes into individual lines
        changes = commit_diff.split("\n")
        # Loop through the changes and print only the lines that start with '+' or '-'
        for change in changes:
            change = change.strip()
            #Filter lines we dont want, like header rows or comments, or file stuff, or empty lines
            if change.startswith(("---", "+++")) or ("#" in change) or ("$" in change) or not change.strip("+-"):
                continue
            elif change.startswith("+"):
                icao_reg = tuple(change.strip("+").split(",")[0:2])
                print("Added", icao_reg, commit_datetime)
                record_history[icao_reg] = {"added_dt": commit_datetime}
            elif change.startswith("-"):
                icao_reg = tuple(change.strip("-").split(",")[0:2])
                print("Removed", icao_reg, commit_datetime)
                record_history[icao_reg]['removed_dt'] = commit_datetime

    except git.GitCommandError:
        # Handle the case where 'git show' fails for the given commit
        continue

import csv

# Define the header
header = ['icao', 'reg', 'added_dt', "removed_dt"]

# Open the file in write mode
with open('pia_history.csv', 'w', newline='') as file:
    writer = csv.writer(file)

    # Write the header
    writer.writerow(header)
    print(record_history)
    for icao_reg, info in record_history.items():
        icao, reg = icao_reg
        print(icao, reg, info)
        writer.writerow([icao, reg, info['added_dt'], info.get("removed_dt")])
