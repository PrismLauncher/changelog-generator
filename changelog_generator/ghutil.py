from typing import Generator, List

from github.Milestone import Milestone
from github.PullRequest import PullRequest
from github.Repository import Repository


def find_milestone_by_name(repo: Repository, milestone_name: str) -> Milestone:
    for milestone in repo.get_milestones():
        if milestone.title == milestone_name:
            return milestone
    return None


def get_prs(
    repo: Repository, only_merged=True, **kwargs
) -> Generator[PullRequest, None, None]:
    issues = repo.get_issues(**kwargs)
    prs: List[PullRequest] = []

    for issue in issues:
        if issue.pull_request:
            pr = issue.as_pull_request()
            if not only_merged or pr.merged:
                yield pr
