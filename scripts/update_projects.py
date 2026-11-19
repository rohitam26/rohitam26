#!/usr/bin/env python3
"""
Update latest repositories list in GitHub Profile README.

Fetches public repositories for a GitHub user using the GitHub REST API,
filters out forks, archived repos, and the profile repository itself,
sorts by most recently updated, enriches descriptions and primary languages,
and updates the marked section in README.md.

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
from typing import Dict, List, Optional, Tuple

START_MARKER = "<!-- PROJECTS:START -->"
END_MARKER = "<!-- PROJECTS:END -->"
API_URL_TEMPLATE = "https://api.github.com/users/{username}/repos"
LANGUAGES_URL_TEMPLATE = "https://api.github.com/repos/{username}/{repo}/languages"

# Non-programming languages and documentation formats to exclude
EXCLUDED_LANGUAGES = {
    "markdown",
    "documentation",
    "text",
    "pdf",
    "tex",
    "roff",
}

# Verified repository registry: accurate, specific descriptions (8–18 words)
# and primary/secondary languages based on source code and laboratory coursework.
REPO_REGISTRY: Dict[str, Dict[str, str]] = {
    "Web-Technology-and-Mobile-Applications-Laboratory": {
        "description": "Client-side web interfaces, Java servlets, Android mobile components, and interactive web application experiments.",
        "language": "HTML, Java",
    },
    "Operating-Systems-Laboratory": {
        "description": "System programming, process scheduling, inter-process communication, and memory virtualization laboratory implementations in C.",
        "language": "C, Shell",
    },
    "Object-Oriented-Programming-with-Java-Laboratory": {
        "description": "Core object-oriented programming principles, modern Java collections, exception handling, and JDBC database applications.",
        "language": "Java",
    },
    "Foundations-of-Machine-Learning-Laboratory": {
        "description": "Supervised and unsupervised learning algorithms, regression models, ensemble classifiers, and dimensionality reduction in Python.",
        "language": "Python",
    },
    "Computer-Networks-Laboratory": {
        "description": "Socket programming, packet sniffing, network routing protocols, and diagnostic networking experiments across layers.",
        "language": "Python, C",
    },
    "Principles-Of-Artificial-Intelligence-Laboratory": {
        "description": "Classical AI algorithms covering heuristic search, constraint satisfaction, game trees, fuzzy logic, and Prolog.",
        "language": "Python, Prolog",
    },
    "Python-Programming-Laboratory": {
        "description": "Core syntax, data structures, recursion, file operations, and vectorized numerical computing using Python.",
        "language": "Python",
    },
    "Database-Management-Systems-Laboratory": {
        "description": "Relational schema design, complex SQL queries, PL/SQL procedures, triggers, and MongoDB NoSQL database operations.",
        "language": "SQL, PL/SQL",
    },
    "Design-and-Analysis-of-Algorithms-Laboratory": {
        "description": "Algorithm design paradigms, asymptotic analysis, divide and conquer, greedy strategies, and dynamic programming in C.",
        "language": "C",
    },
    "Data-Analytics-and-Visualization-Laboratory": {
        "description": "Exploratory data analysis, statistical data wrangling, and multi-variable visual dashboards using Pandas and Seaborn.",
        "language": "Python",
    },
    "Deep-Learning-Laboratory": {
        "description": "Neural network architectures, optimization techniques, computer vision, sequence models, and deep generative implementations in Python.",
        "language": "Python",
    },
    "YatraSaathi": {
        "description": "Location-aware journey companion with multi-stop GPS tracking, proximity arrival alarms, and safety check-ins.",
        "language": "Dart",
    },
    "Low-Code-Application-Development-using-Zoho-Creator": {
        "description": "Academic coursework planner and milestone tracking application built on the Zoho Creator cloud platform.",
        "language": "Deluge",
    },
    "UC-05_automation-workload": {
        "description": "Automation workload estimation and preview engine with rule validation and idempotent execution.",
        "language": "Python, TypeScript",
    },
    "stockguard": {
        "description": "Distributed inventory reservation and checkout reliability engine with atomic conditional allocations and saga orchestration.",
        "language": "Python, SQL",
    },
}


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


def make_github_request(
    url: str,
    token: Optional[str] = None,
    username: str = "rohitam26",
    timeout: int = 15,
) -> Optional[dict | list]:
    """Execute a GET request against the GitHub REST API."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": f"github-profile-updater/{username}",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        # Silently fail or log for optional enrichments
        return None
    return None


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


def resolve_repository_language(
    repo: Dict,
    username: str,
    token: Optional[str] = None,
) -> str:
    """
    Determine primary (and optionally secondary) programming language.
    Checks:
    1. GitHub Languages API
    2. Verified repository registry
    3. Fallback based on repository metadata
    """
    repo_name = repo.get("name", "")

    # 1. Query GitHub Languages API if token or live connection is available
    languages_data = None
    if token or not repo_name.startswith("mock-"):
        lang_url = LANGUAGES_URL_TEMPLATE.format(username=username, repo=repo_name)
        languages_data = make_github_request(lang_url, token=token, username=username)

    if isinstance(languages_data, dict) and languages_data:
        # Filter excluded/non-programming languages
        valid_langs = []
        for lang_name, byte_count in languages_data.items():
            clean_name = lang_name.strip()
            # If Jupyter Notebook, recognize as Python
            if clean_name.lower() == "jupyter notebook":
                clean_name = "Python"
            if clean_name.lower() in EXCLUDED_LANGUAGES:
                continue
            valid_langs.append((clean_name, byte_count))

        if valid_langs:
            # Aggregate byte counts for duplicate normalized names (e.g. Python)
            aggregated = {}
            for name, count in valid_langs:
                aggregated[name] = aggregated.get(name, 0) + count

            sorted_langs = sorted(aggregated.items(), key=lambda x: x[1], reverse=True)
            primary = sorted_langs[0][0]

            # If a secondary language has significant presence (> 15%), include it
            if len(sorted_langs) > 1 and sorted_langs[1][1] > (sorted_langs[0][1] * 0.15):
                secondary = sorted_langs[1][0]
                return f"{primary}, {secondary}"
            return primary

    # 2. Check verified repository registry
    if repo_name in REPO_REGISTRY:
        return REPO_REGISTRY[repo_name]["language"]

    # 3. Check language field reported on repo object
    base_lang = repo.get("language")
    if base_lang and base_lang.strip():
        clean_base = base_lang.strip()
        if clean_base.lower() == "jupyter notebook":
            return "Python"
        if clean_base.lower() not in EXCLUDED_LANGUAGES:
            return clean_base

    # 4. Fallback: check if it's purely documentation
    return "Documentation"


def resolve_repository_description(
    repo: Dict,
    username: str,
    token: Optional[str] = None,
) -> str:
    """
    Obtain a concise, specific description (approx 8–18 words).
    Checks:
    1. Verified repository registry
    2. GitHub repository description (if specific and non-generic)
    3. Repository README overview extraction
    """
    repo_name = repo.get("name", "")

    # Check verified registry first for maximum precision and adherence to word limits
    if repo_name in REPO_REGISTRY:
        return REPO_REGISTRY[repo_name]["description"]

    # Check existing GitHub description
    raw_desc = repo.get("description")
    if raw_desc and raw_desc.strip():
        cleaned_desc = " ".join(raw_desc.strip().split())
        # Avoid generic GitHub placeholder descriptions
        if not cleaned_desc.startswith("Contribute to") and "development by creating an account" not in cleaned_desc:
            word_count = len(cleaned_desc.split())
            if 8 <= word_count <= 22:
                return cleaned_desc

    # Fallback to generating a specific summary based on repository name and language
    lang = resolve_repository_language(repo, username, token)
    formatted_name = repo_name.replace("-", " ").replace("_", " ")
    return f"Implementations, coursework exercises, and practical projects for {formatted_name} in {lang}."


def generate_markdown(
    repos: List[Dict],
    username: str = "rohitam26",
    token: Optional[str] = None,
) -> str:
    """
    Generate clean, dark-mode compatible Markdown table for repository entries
    with enriched descriptions and languages.
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
        url = repo.get("html_url", f"https://github.com/{username}/{name}")

        description = resolve_repository_description(repo, username=username, token=token)
        desc_text = escape_markdown_cell(description)

        language = resolve_repository_language(repo, username=username, token=token)
        lang_text = escape_markdown_cell(language)

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
        try:
            raw_repos = fetch_repositories(username=username, token=token)
        except Exception as exc:
            print(f"GitHub API fetch failed: {exc}. Using fallback registry if possible.", file=sys.stderr)
            # If API is rate-limited or offline, construct from registry of known repositories
            raw_repos = [
                {
                    "name": name,
                    "html_url": f"https://github.com/{username}/{name}",
                    "description": meta["description"],
                    "language": meta["language"].split(",")[0].strip(),
                    "fork": False,
                    "archived": False,
                    "updated_at": f"2026-11-{15 - i:02d}T12:00:00Z",
                }
                for i, (name, meta) in enumerate(REPO_REGISTRY.items())
                if name != "UC-05_automation-workload"
            ]

    print(f"Retrieved {len(raw_repos)} total repositories.")
    selected_repos = filter_and_sort_repositories(
        raw_repos, username=username, limit=limit
    )
    print(f"Filtered down to {len(selected_repos)} repositories (limit: {limit}).")

    new_section = generate_markdown(selected_repos, username=username, token=token)
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
