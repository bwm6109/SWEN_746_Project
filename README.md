# SWEN_746_Project
Project for Master's class SWEN 746 - Model Driven Development

Milestones

RM0
    Repo Initialization
    Virtual environment and requirements
    
RM1 (Commit Fetcher)
    Implemented fetch_commits(repo_name, max_commits)
    CLI interface fetch_commits
    Unit tests with Pytest and dummy objects
    CSV export of GitHub commit data

RM2 (Issue Fetcher)
    Implemented fetch_issues(repo_name, state, max_issues)
    Skips pull requests and normalizes to ISO dates
    CLI interface fetch_issues
    Unit tests with Pytest and dummy objects

RM3 (Merge and Summarize Commits and Issues)
    Implemented merge_and_summarize(commits_df: pd.DataFrame, issues_df: pd.DataFrame)
    Prints top committers, issue close rate, and average issue open duration
    CLI interface merge_and_summarize
    Added given unit test
    Usage: python -m src.repo_miner summarize --commits commits.csv --issues issues.csv
    