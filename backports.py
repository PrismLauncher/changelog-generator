import os
from github import Github, PullRequest
from typing import List

REPO = "PrismLauncher/PrismLauncher"
MILESTONE = "7.2"
TOKEN = os.environ["GITHUB_TOKEN"]


def getter(index):
    return lambda x: x[index]


if __name__ == "__main__":
    output = []

    g = Github(TOKEN)

    repo = g.get_repo(REPO)

    release_milestone = None

    for milestone in repo.get_milestones():
        if milestone.title == MILESTONE:
            release_milestone = milestone
            break

    commits = []

    for issue in repo.get_issues(milestone=release_milestone, state="all"):
        if issue.pull_request:
            pr = issue.as_pull_request()

            if not pr.merged:
                print(f"skip {pr.id}")
                continue

            commit = repo.get_commit(pr.merge_commit_sha)

            a = (commit.commit.committer.date, commit.sha)

            commits.append(a)
            print(a)

    commits_sorted = [*sorted(commits, key=getter(0))]

    print(" ".join([*map(getter(1), commits_sorted)]))
