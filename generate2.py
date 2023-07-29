from github import Github
from github.Label import Label
from github.PullRequest import PullRequest
from typing import List
import re

REPO = "PrismLauncher/PrismLauncher"
MILESTONE = "8.0"
TOKEN = os.environ["GITHUB_TOKEN"]

LABEL_PREFIX = "changelog:"
MERGED_CATEGORY = "merged"

PARENT_PATTERN = r"Parent PR:\s*#(\d+)"
CATEGORY_MAP = [
    ("added", "## Added"),
    ("changed", "## Changed"),
    ("fixed", "## Fixed"),
    ("removed", "## Removed"),
]


def pr_link(pr: PullRequest):
    return f"[#{pr.number}](https://github.com/{REPO}/pull/{pr.number})"


def author_link(author: str):
    return f"[@{author}](https://github.com/{author})"


def human_list(x: List[str]):
    if len(x) < 1:
        return "WTF??"
    elif len(x) == 1:
        return x[0]
    y = ", ".join(x[:-1])
    y += f" and {x[-1]}"
    return y


entries = []


class Change:
    def __init__(self, prs: List[PullRequest], category: str):
        self.prs = prs
        self.category = category

    def pr(self):
        return self.prs[0]

    def number(self):
        return self.pr().number

    def title(self):
        return self.pr().title

    def __repr__(self):
        return f"{self.pr().title} (#{self.number()})"

    def changelog_entry(self):
        authors = set()
        for pr in self.prs:
            authors.add(pr.user.login)
            for c in pr.get_commits():
                if not c.author:
                    print(f"Commit {c} from {self} does not have an author")
                    continue
                authors.add(c.author.login)

        autor_links = [*map(author_link, authors)]
        pr_links = [*map(pr_link, self.prs)]

        return (
            f"- {self.title()} by {human_list(autor_links)} in {human_list(pr_links)}"
        )


def get_category_from_labels(labels: List[Label]):
    for label in labels:
        if label.name.startswith(LABEL_PREFIX):
            return label.name[len(LABEL_PREFIX) :]


def categorize_pr(pr: PullRequest):
    category = get_category_from_labels(pr.labels)
    return Change([pr], category)


if __name__ == "__main__":
    output = []

    g = Github(TOKEN)

    repo = g.get_repo(REPO)

    release_milestone = None

    for milestone in repo.get_milestones():
        if milestone.title == MILESTONE:
            release_milestone = milestone
            break

    issues = repo.get_issues(milestone=release_milestone, state="all")
    prs = map(
        lambda issue: issue.as_pull_request(),
        [*filter(lambda issue: issue.pull_request, issues)],
    )
    merged_prs = [*filter(lambda pr: pr.merged, prs)]
    changes = [*map(categorize_pr, merged_prs)]

    merged_changes = [
        *filter(lambda change: change.category == MERGED_CATEGORY, changes)
    ]
    top_level_changes = [
        *filter(lambda change: change.category != MERGED_CATEGORY, changes)
    ]

    for change in merged_changes:
        m = re.match(PARENT_PATTERN, change.pr().body)

        if m is not None:
            parent_number = int(m.group(1))

            found_parent = False
            for other_change in top_level_changes:
                if other_change.number() == parent_number:
                    other_change.prs += change.prs
                    found_parent = True
                    break
            if not found_parent:
                print(
                    f"'{change}' parent (#{parent_number}) was not found in this milestone"
                )
        else:
            print(f"'{change}' does not define a parent")

    final_changes = sorted(top_level_changes, key=lambda x: x.title())
    print("---")

    for category, title in CATEGORY_MAP:
        print(title)
        print()

        for change in final_changes:
            if change.category == category:
                print(change.changelog_entry())

        print()
