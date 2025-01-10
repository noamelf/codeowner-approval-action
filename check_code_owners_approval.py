# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "codeowners",
#     "pygithub",
# ]
# ///
import argparse
import os
import sys
import logging
from functools import lru_cache
from collections.abc import Sequence

from codeowners import CodeOwners
from github import Github, Repository, PullRequest, Organization

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def parse_args() -> argparse.Namespace:
    """
    Parses and returns command line arguments.
    """
    parser = argparse.ArgumentParser(description="Check if all code owners have approved a PR")
    parser.add_argument("--pr-number", required=True, type=int, help="Pull Request number")
    parser.add_argument("--repo-name", required=True, type=str, help="Repository name in the format 'org/repo'")
    return parser.parse_args()


def get_codeowners(repo: Repository.Repository) -> CodeOwners:
    """
    Fetches the CODEOWNERS file from the repository and returns a CodeOwners object.
    Searches in standard locations.
    """
    codeowners_paths = [".github/CODEOWNERS", "docs/CODEOWNERS", "CODEOWNERS"]
    codeowners_content: str | None = None

    for path in codeowners_paths:
        try:
            contents = repo.get_contents(path)
            if isinstance(contents, list):
                contents = contents[0]
            codeowners_content = contents.decoded_content.decode("utf-8")
            logging.info(f"Found CODEOWNERS file at: {path}")
            break
        except Exception:
            continue

    if codeowners_content is None:
        raise FileNotFoundError("CODEOWNERS file not found in the repository.")

    return CodeOwners(codeowners_content)


def get_modified_files(pr: PullRequest.PullRequest) -> list[str]:
    """
    Returns a list of filenames modified in the pull request.
    """
    return [file.filename for file in pr.get_files()]


def get_approved_reviews(pr: PullRequest.PullRequest) -> set[str]:
    """
    Returns a list of users who have approved the PR.
    Considers only the latest review state per user.
    """
    reviews = pr.get_reviews()
    approvals = set(review.user.login for review in reviews if review.state == "APPROVED")

    logging.info(f"Fetched approved reviews: {approvals}")

    return approvals


@lru_cache(maxsize=None)
def get_team_members(org: Organization.Organization, team_slug: str) -> list[str]:
    """
    Fetches the members of a GitHub team by its slug.
    """
    team = org.get_team_by_slug(team_slug)
    members = [member.login for member in team.get_members()]
    logging.debug(f"Fetched team members for team: {team_slug}")
    return members


def get_file_owners(codeowners: CodeOwners, filepath: str) -> Sequence[tuple[str, str]]:
    """
    Returns a list of owners for the given file path.
    """
    return codeowners.of(filepath)


def get_missing_approvals_for_file(
    file: str, codeowners: CodeOwners, approved_reviews: set[str], org: Organization.Organization | None
) -> list[str]:
    """
    Checks if all owners (teams and individuals) for a file have approved the PR.
    Returns a list of missing approvals.
    """
    missing_approvals = []
    file_owners = get_file_owners(codeowners, file)

    for owner_type, owner_name in file_owners:
        if owner_type == "TEAM":
            team_slug = owner_name.split("/")[-1]
            team_members = get_team_members(org, team_slug)
            if not any(member in approved_reviews for member in team_members):
                missing_approvals.append(owner_name)
        else:
            if owner_name.replace("@", "") not in approved_reviews:
                missing_approvals.append(owner_name)

    return missing_approvals


def gather_missing_approvals(
    modified_files: list[str],
    codeowners: CodeOwners,
    approved_reviews: set[str],
    org: Organization.Organization | None,
) -> dict[str, list[str]]:
    """
    Checks approvals for all modified files.
    Returns a dictionary with files as keys and lists of missing approvals as values.
    """
    missing_approvals: dict[str, list[str]] = {}
    for file in modified_files:
        missing = get_missing_approvals_for_file(file, codeowners, approved_reviews, org)
        if missing:
            missing_approvals[file] = missing
    return missing_approvals


def check_all_owners_approved(args: argparse.Namespace) -> bool:
    """
    Main function to check if all code owners have approved the PR.
    Returns True if all approvals are in place, otherwise False.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise EnvironmentError("GITHUB_TOKEN environment variable not found.")

    # Initialize GitHub API client
    g = Github(github_token)
    repo: Repository.Repository = g.get_repo(args.repo_name)
    pr: PullRequest.PullRequest = repo.get_pull(args.pr_number)
    try:
        org: Organization.Organization | None = g.get_organization(args.repo_name.split("/")[0])
    except Exception:
        org = None

    # Fetch necessary data
    codeowners = get_codeowners(repo)
    modified_files = get_modified_files(pr)
    approved_reviews = get_approved_reviews(pr)

    # Gather missing approvals
    missing_approvals = gather_missing_approvals(modified_files, codeowners, approved_reviews, org)

    if missing_approvals:
        # Output GitHub Action error annotations for missing approvals
        for file, approvers in missing_approvals.items():
            print(f"::error::Missing approvals for {file} from: {', '.join(approvers)}")
        return False  # Indicate failure
    else:
        logging.info("SUCCESS: All code owners have approved the PR.")
        return True  # Indicate success


if __name__ == "__main__":
    args = parse_args()
    try:
        success = check_all_owners_approved(args)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"::error::{str(e)}")
        sys.exit(1)
