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

    args = parser.parse_args()

    # Dispatch based on selected command
    if args.command == "fetch-commits":
        df = fetch_commits(args.repo, args.max_commits)
        df.to_csv(args.out, index=False)
        print(f"Saved {len(df)} commits to {args.out}")


if __name__ == "__main__":
    main()
