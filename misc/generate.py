from github import Github, PullRequest
from typing import List

REPO = "PrismLauncher/PrismLauncher"
MILESTONE = "7.2"
TOKEN = os.environ["GITHUB_TOKEN"]


def pr_link(pr):
    return f"[#{pr}](https://github.com/PrismLauncher/PrismLauncher/pull/{pr})"


def author_link(author):
    return f"[@{author}](https://github.com/{author})"


def human_list(x: List[str]):
    if len(x) < 1:
        return "WTF??"
    elif len(x) == 1:
        return x[0]
    y = ", ".join(x[:-1])
    y += f" and {x[-1]}"
    return y


def process_pr(pr: PullRequest):
    authors = [author_link(pr.user.login)]
    commits = pr.get_commits()
    for c in commits:
        if not c.author:
            print(c)
            continue
        login = author_link(c.author.login)
        # this is ugly, but it is the best way to maintain the order of the list without dumb hacks
        if login not in authors:
            authors.append(login)

    return f" - {pr.title} by {human_list(authors)} in {pr_link(pr.number)}"


if __name__ == "__main__":
    output = []

    g = Github(TOKEN)

    repo = g.get_repo(REPO)

    release_milestone = None

    for milestone in repo.get_milestones():
        if milestone.title == MILESTONE:
            release_milestone = milestone
            break

    for issue in repo.get_issues(milestone=release_milestone, state="all"):
        if issue.pull_request:
            output.append(process_pr(issue.as_pull_request()))

    for x in sorted(output):
        print(x)
