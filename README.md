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
    