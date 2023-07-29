from typing import Generator, List

from github.PullRequest import PullRequest


def pr_link(pr: PullRequest, repo_path: str = "PrismLauncher/PrismLauncher"):
    return f"[#{pr.number}](https://github.com/{repo_path}/pull/{pr.number})"


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
