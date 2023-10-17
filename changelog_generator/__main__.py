from github import Github
from github.Label import Label
from github.PullRequest import PullRequest
from github.Repository import Repository

from typing import List
import re
import os
import argparse

from .ghutil import find_milestone_by_name, get_prs
from .util import pr_link, author_link, human_list


LABEL_PREFIX = "changelog:"
MERGED_CATEGORY = "merged"

PARENT_PATTERN = r"Parent PR:\s*#(\d+)"
CATEGORY_MAP = [
    ("added", "## Added"),
    ("changed", "## Changed"),
    ("fixed", "## Fixed"),
    ("removed", "## Removed"),
]


entries = []


class Change:
    def __init__(self, prs: List[PullRequest], category: str):
        self.prs = prs
        self.category = category

    def merge(self, other):
        self.prs += other.prs

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
    return "unknown"


def categorize_pr(pr: PullRequest):
    category = get_category_from_labels(pr.labels)
    return Change([pr], category)


def merge_child_changes(children: List[Change], parents: List[Change]):
    for change in children:
        m = re.match(PARENT_PATTERN, change.pr().body)

        assert m, f"'{change}' does not define a parent"

        parent_number = int(m.group(1))

        found_parent = False
        for other_change in parents:
            if other_change.number() == parent_number:
                other_change.merge(change)
                found_parent = True
                break
        assert (
            found_parent
        ), f"'{change}' parent (#{parent_number}) was not found in this milestone"


def generate(repo_name: str, milestone: str, token: str):
    g = Github(token)

    repo = g.get_repo(repo_name)

    release_milestone = find_milestone_by_name(repo, milestone)

    assert (
        release_milestone is not None
    ), f"Milestone {milestone} not found in repository {repo.url}"

    prs = get_prs(repo, milestone=release_milestone, state="all")
    changes = [*map(categorize_pr, prs)]

    merged_changes = [
        *filter(lambda change: change.category == MERGED_CATEGORY, changes)
    ]
    top_level_changes = [
        *filter(lambda change: change.category != MERGED_CATEGORY, changes)
    ]

    merge_child_changes(merged_changes, top_level_changes)

    final_changes = sorted(top_level_changes, key=lambda x: x.title())
    print("---")

    for category, title in CATEGORY_MAP:
        print(title)
        print()

        for change in final_changes:
            if change.category == category:
                print(change.changelog_entry())

        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("milestone")

    args = parser.parse_args()

    token = os.environ["GITHUB_TOKEN"]

    generate(args.repo, args.milestone, token)


if __name__ == "__main__":
    main()
