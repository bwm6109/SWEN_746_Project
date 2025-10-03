#!/usr/bin/env python3
"""
repo_miner.py

A command-line tool to:
  1) Fetch and normalize commit data from GitHub

Sub-commands:
  - fetch-commits
"""

import os
import argparse
from typing import List, Dict

import pandas as pd
from github import Github


def fetch_commits(repo_name: str, max_commits: int = None) -> pd.DataFrame:
    """
    Fetch up to `max_commits` from the specified GitHub repository.
    Returns a DataFrame with columns: sha, author, email, date, message.

    Parameters
    repo_name : str
        "owner/repo" format - EX bwm6109/SWEN_746_Project
    max_commits : int, optional
        Maximum number of commits to fetch from GitHub
        EX --max 5


    :returns: pd.DataFrame
    A DataFrame with columns: sha, author, email, date, message.
    """
    # 1) Read GitHub token from environment
    github_token = os.environ.get("GITHUB_TOKEN")

    # 2) Initialize GitHub client and get the repo
    github_client = Github(github_token)
    repo = github_client.get_repo(repo_name)

    # 3) Fetch commit objects (paginated by PyGitHub)
    all_commits = repo.get_commits()

    # 4) Normalize each commit into a record dict
    commit_rows: List[Dict[str, object]] = []
    count = 0
    for commit in all_commits:
        commit_data = getattr(commit, "commit", None)
        current_sha = None
        current_author = None
        current_email = None
        current_date = None
        current_date_iso = None
        current_message = None
        if commit_data is not None:
            author_object = getattr(commit_data, "author", None)
            if author_object is not None:
                current_author = getattr(author_object, "name", None)
                current_email = getattr(author_object, "email", None)
                current_date = getattr(author_object, "date", None)
                if current_date is not None:
                    current_date_iso = current_date.isoformat()
            current_message = getattr(commit_data, "message", None)
            if current_message is not None:
                current_message = current_message.splitlines()[0]
            current_sha = commit.sha
            print(current_sha)

        commit_rows.append({
            "sha": current_sha,
            "author": current_author,
            "email": current_email,
            "date": current_date_iso,
            "message": current_message,
        })
        count += 1
        if max_commits is not None:
            if count >= max_commits:
                break

    # 5) Build DataFrame from records
    return pd.DataFrame(commit_rows, columns=["sha", "author", "email", "date", "message"])

def fetch_issues(repo_name: str, state: str = "all", max_issues: int = None) -> pd.DataFrame:
    """
    Fetch up to `max_issues` from the specified GitHub repository (issues only).

    Paramaters:
    repo_name : str - owner/repo format - EX bwm6109/SWEN_746_Project
    state : str - ["all", "open", "closed"]
    max_issues : int, optional


    Returns a DataFrame with columns: id, number, title, user, state, created_at, closed_at, comments.
    pd.DataFrame - table with columns for id, number, title, user, state, created_at, closed_at, comments, and open_duration_days

    Made sure dates are converted properly and PRs are skipped
    """

    # 1) Read GitHub token
    github_token = os.environ.get("GITHUB_TOKEN")

    # 2) Initialize client and get the repo
    github_client = Github(github_token)
    repo = github_client.get_repo(repo_name)

    # 3) Fetch issues, filtered by state ('all', 'open', 'closed')
    issues = repo.get_issues(state=state)

    # 4) Normalize each issue (skip PRs)
    record_rows: List[Dict[str, object]] = []
    count = 0
    for issue in issues:
        # Skip pull requests
        if getattr(issue, "pull_request", None) is not None:
            continue

        if getattr(issue, "created_at", None) is not None:
            created_iso = getattr(issue, "created_at", None).isoformat()
        else:
            created_iso = None
        if getattr(issue, "closed_at", None) is not None:
            closed_iso = getattr(issue, "closed_at", None).isoformat()
        else:
            closed_iso = None

        # Append records
        if created_iso is not None and closed_iso is not None:
            issue_created = issue.created_at
            issue_closed = issue.closed_at
            days_open = (issue_closed - issue_created).days
        else:
            days_open = None

        record_rows.append(
            {
                "id": getattr(issue, "id", None),
                "number": getattr(issue, "number", None),
                "title": getattr(issue, "title", None),
                "user": getattr(issue, "user", None),
                "state": getattr(issue, "state", None),
                "created_at": created_iso,
                "closed_at": closed_iso,
                "comments": getattr(issue, "comments", None),
                "open_duration_days": days_open,
            }
        )
        count += 1
        if max_issues is not None and count >= max_issues:
            break

    # 5) Build DataFrame
    return pd.DataFrame(record_rows, columns=[
        "id", "number", "title", "user", "state", "created_at", "closed_at", "comments", "open_duration_days"
    ])

def main():
    """
    Parse command-line arguments and dispatch to sub-commands.
    """
    parser = argparse.ArgumentParser(
        prog="repo_miner",
        description="Fetch GitHub commits/issues and summarize them"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-command: fetch-commits
    c1 = subparsers.add_parser("fetch-commits", help="Fetch commits and save to CSV")
    c1.add_argument("--repo", required=True, help="Repository in owner/repo format")
    c1.add_argument("--max", type=int, dest="max_commits",
                    help="Max number of commits to fetch")
    c1.add_argument("--out", required=True, help="Path to output commits CSV")


    c2 = subparsers.add_parser("fetch-issues", help="Fetch issues and save to CSV")
    c2.add_argument("--repo", required=True, help="Repository in owner/repo format")
    c2.add_argument("--state", choices=["all", "open", "closed"], default="all",
                    help="Filter issues by state")
    c2.add_argument("--max", type=int, dest="max_issues",
                    help="Max number of issues to fetch")
    c2.add_argument("--out", required=True, help="Path to output issues CSV")

    args = parser.parse_args()

    # Dispatch based on selected command
    if args.command == "fetch-commits":
        df = fetch_commits(args.repo, args.max_commits)
        df.to_csv(args.out, index=False)
        print(f"Saved {len(df)} commits to {args.out}")

    elif args.command == "fetch-issues":
        df = fetch_issues(args.repo, args.state, args.max_issues)
        df.to_csv(args.out, index=False)
        print(f"Saved {len(df)} issues to {args.out}")

if __name__ == "__main__":
    main()
