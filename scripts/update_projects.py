#!/usr/bin/env python3
"""
Update latest repositories list in GitHub Profile README.

Fetches public repositories for a GitHub user using the GitHub REST API,
filters out forks, archived repos, and the profile repository itself,
sorts by most recently updated, and updates the marked section in README.md.

Markers:
<!-- PROJECTS:START -->
<!-- PROJECTS:END -->
"""

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

START_MARKER = "<!-- PROJECTS:START -->"
END_MARKER = "<!-- PROJECTS:END -->"
API_URL_TEMPLATE = "https://api.github.com/users/{username}/repos"


def escape_markdown_cell(text: str) -> str:
    """Sanitize and escape text for insertion into a Markdown table cell."""
    if not text:
        return ""
    # Collapse consecutive whitespace and strip
    cleaned = " ".join(text.split())
    # Escape pipe characters to avoid breaking Markdown table structure
    cleaned = cleaned.replace("|", "\\|")
    # Escape HTML tags
    cleaned = cleaned.replace("<", "&lt;").replace(">", "&gt;")
    return cleaned


def fetch_repositories(
    username: str,
    token: Optional[str] = None,
    api_url: Optional[str] = None,
) -> List[Dict]:
    """
    Fetch all public repositories for the specified user with pagination.
    """
    base_url = api_url or API_URL_TEMPLATE.format(username=username)
    page = 1
    per_page = 100
    all_repos: List[Dict] = []

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": f"github-profile-updater/{username}",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    while True:
        url = f"{base_url}?per_page={per_page}&page={page}&sort=updated&direction=desc"
        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                status = response.status
                if status != 200:
                    raise RuntimeError(f"GitHub API returned unexpected HTTP status: {status}")
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            err_msg = err.read().decode("utf-8", errors="ignore")
            if err.code == 403 and "rate limit" in err_msg.lower():
                raise RuntimeError(
                    f"GitHub API rate limit exceeded. Consider providing GITHUB_TOKEN.\nDetails: {err_msg}"
                ) from err
            raise RuntimeError(f"HTTP {err.code} while fetching {url}: {err_msg}") from err
        except urllib.error.URLError as err:
            raise RuntimeError(f"Network error while connecting to GitHub API: {err.reason}") from err
        except json.JSONDecodeError as err:
            raise RuntimeError(f"Failed to parse GitHub API JSON response: {err}") from err

        if not isinstance(payload, list):
            raise RuntimeError(f"Expected a list of repositories, got: {type(payload)}")

        if not payload:
            break

        all_repos.extend(payload)

        # Check if we reached the last page
        if len(payload) < per_page:
            break

        page += 1

    return all_repos


def filter_and_sort_repositories(
    repos: List[Dict],
    username: str,
    limit: int = 8,
) -> List[Dict]:
    """
    Filter repositories:
    - Exclude forks
    - Exclude archived
    - Exclude profile repository (same name as username)
    Sort by updated_at descending and take top `limit`.
    """
    filtered = []
    target_username = username.strip().lower()

    for repo in repos:
        # Exclude forks
        if repo.get("fork", False):
            continue

        # Exclude archived
        if repo.get("archived", False):
            continue

        # Exclude profile repository
        repo_name = repo.get("name", "").strip()
        if repo_name.lower() == target_username:
            continue

        filtered.append(repo)

    # Sort by updated_at ISO 8601 string descending
    filtered.sort(
        key=lambda r: r.get("updated_at") or r.get("pushed_at") or "",
        reverse=True,
    )

    return filtered[:limit]


def generate_markdown(repos: List[Dict]) -> str:
    """
    Generate clean, dark-mode compatible Markdown table for repository entries.
    """
    if not repos:
        return "\n_No public repositories found._\n"

    lines = [
        "",
        "| Repository | Description | Primary Language |",
        "| :--- | :--- | :--- |",
    ]

    for repo in repos:
        name = escape_markdown_cell(repo.get("name", "Untitled"))
        url = repo.get("html_url", f"https://github.com/rohitam26/{name}")
        description = repo.get("description")
        if description and description.strip():
            desc_text = escape_markdown_cell(description.strip())
        else:
            desc_text = "_No description provided_"

        language = repo.get("language")
        lang_text = escape_markdown_cell(language.strip()) if language and language.strip() else "—"

        lines.append(f"| [**{name}**]({url}) | {desc_text} | {lang_text} |")

    lines.append("")
    return "\n".join(lines)


def update_readme_content(
    current_content: str,
    new_markdown: str,
    start_marker: str = START_MARKER,
    end_marker: str = END_MARKER,
) -> tuple[str, bool]:
    """
    Replace the section between start_marker and end_marker.
    Returns (updated_content, has_changed).
    """
    if start_marker not in current_content:
        raise ValueError(f"Start marker '{start_marker}' not found in README.")
    if end_marker not in current_content:
        raise ValueError(f"End marker '{end_marker}' not found in README.")

    start_idx = current_content.index(start_marker) + len(start_marker)
    end_idx = current_content.index(end_marker)

    if start_idx > end_idx:
        raise ValueError(
            f"Start marker '{start_marker}' appears after end marker '{end_marker}'."
        )

    existing_section = current_content[start_idx:end_idx]

    # Normalize newlines for strict comparison
    normalized_existing = existing_section.strip("\r\n")
    normalized_new = new_markdown.strip("\r\n")

    if normalized_existing == normalized_new:
        return current_content, False

    # Format cleanly with surrounding newlines
    replacement = f"\n{normalized_new}\n"
    updated_content = (
        current_content[:start_idx]
        + replacement
        + current_content[end_idx:]
    )

    return updated_content, True


def run(
    readme_path: Path,
    username: str,
    limit: int = 8,
    token: Optional[str] = None,
    fixture_path: Optional[Path] = None,
    dry_run: bool = False,
) -> bool:
    """
    Main orchestration function.
    """
    if not readme_path.exists():
        raise FileNotFoundError(f"README file not found at: {readme_path}")

    current_content = readme_path.read_text(encoding="utf-8")

    # Load repositories from fixture (if specified) or GitHub REST API
    if fixture_path:
        print(f"Loading repository data from fixture: {fixture_path}")
        raw_repos = json.loads(fixture_path.read_text(encoding="utf-8"))
    else:
        print(f"Fetching public repositories for '{username}' from GitHub API...")
        raw_repos = fetch_repositories(username=username, token=token)

    print(f"Retrieved {len(raw_repos)} total repositories.")
    selected_repos = filter_and_sort_repositories(
        raw_repos, username=username, limit=limit
    )
    print(f"Filtered down to {len(selected_repos)} repositories (limit: {limit}).")

    new_section = generate_markdown(selected_repos)
    updated_content, changed = update_readme_content(
        current_content=current_content,
        new_markdown=new_section,
    )

    if not changed:
        print("No changes detected in the latest repositories section. README remains identical.")
        return False

    if dry_run:
        print("Dry-run enabled: differences detected but not saved to file.")
        print("--- Generated Section ---")
        print(new_section)
        print("--- End Generated Section ---")
        return True

    readme_path.write_text(updated_content, encoding="utf-8")
    print(f"Successfully updated {readme_path} with latest {len(selected_repos)} repositories.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update GitHub Profile README with latest repositories."
    )
    parser.add_argument(
        "--username",
        default="rohitam26",
        help="GitHub username (default: rohitam26)",
    )
    parser.add_argument(
        "--readme",
        type=Path,
        default=Path("README.md"),
        help="Path to README.md (default: README.md)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=8,
        help="Maximum number of repositories to include (default: 8)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub API Token (falls back to GITHUB_TOKEN environment variable)",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=None,
        help="Path to a JSON fixture containing mock repositories (useful for offline testing)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without modifying the README file",
    )

    args = parser.parse_args()

    try:
        run(
            readme_path=args.readme,
            username=args.username,
            limit=args.limit,
            token=args.token,
            fixture_path=args.fixture,
            dry_run=args.dry_run,
        )
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
