#!/usr/bin/env python3
"""
Base16 Theme Updater

This script automates the process of fetching, parsing, and generating Hugo-compatible
markdown files for base16 themes. It queries the official base16 schemes source list,
clones each repository, extracts theme definitions (YAML), and converts them into
markdown files with frontmatter that can be used by the Hugo site.

Flow:
1. Fetch the master list of theme repositories.
2. Clone each repository in parallel (using ThreadPoolExecutor) to a temporary directory.
3. Parse YAML files to extract color schemes.
4. Filter out incomplete themes (missing required base00-base0F keys).
5. Generate individual markdown files (theme_*.md) in the script's directory.

Note:
    - This script requires `git` to be installed and available in the PATH.
    - It uses temporary directories for cloning to ensure a clean state and avoid conflicts.
    - Network errors during cloning are logged but do not stop the entire process.
"""

import json
import logging
import os
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict
from urllib import request

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent
COLOR_KEYS = [
    "base00",
    "base01",
    "base02",
    "base03",
    "base04",
    "base05",
    "base06",
    "base07",
    "base08",
    "base09",
    "base0A",
    "base0B",
    "base0C",
    "base0D",
    "base0E",
    "base0F",
]
SCHEME_LIST_URL = "https://raw.githubusercontent.com/chriskempson/base16-schemes-source/refs/heads/main/list.yaml"


def read_kv(data: str | bytes) -> Dict[str, str]:
    """
    Parses key-value pairs from simple YAML-like content.

    This function manually parses lines in the format `key: value` to avoid
    dependency on an external YAML parser (like PyYAML), keeping the script
    lightweight and standard-library only.

    Args:
        data: The content to parse, as a string or bytes.

    Returns:
        A dictionary containing the parsed key-value pairs. Returns an empty
        dict if no valid pairs are found.
    """
    line_regexp = re.compile(r"^(?P<key>.*): (?P<value>[^#]*)")
    ret = {}
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    for item in data.split("\n"):
        item_str = item.strip()
        match = line_regexp.match(item_str)
        if not match:
            continue
        key = match.group("key").strip()
        value = match.group("value").strip().strip('"')
        ret[key] = value
    return ret


def fetch_repo_list(url: str) -> Dict[str, str]:
    """
    Fetches the authoritative list of base16 scheme repositories.

    Retrieves the YAML list from the official base16-schemes-source repository.
    This list maps scheme names to their GitHub repository URLs.

    Args:
        url: The URL of the scheme list YAML file.

    Returns:
        A dictionary mapping repo names to their Git URLs.
    """
    logger.info(f"Fetching scheme list from {url}")
    try:
        with request.urlopen(url) as response:
            return read_kv(response.read())
    except Exception as e:
        logger.error(f"Failed to fetch repo list: {e}")
        return {}


def process_theme_repo(repo_name: str, repo_url: str) -> Dict[str, Any]:
    """
    Clones a single theme repository and extracts all valid theme definitions.

    This function performs the following steps:
    1. Creates a temporary directory.
    2. Clones the git repository into it (silencing git prompts).
    3. Scans for `*.yaml` files within the cloned repo.
    4. Parses each file using `read_kv`.

    Args:
        repo_name: The name of the repository (for logging).
        repo_url: The git URL to clone.

    Returns:
        A dictionary where keys are theme filenames (stem) and values are the
        parsed theme data dictionaries. Returns an empty dict on failure.
    """
    repo_themes = {}
    logger.info(f"Processing repo: {repo_name} ({repo_url})")

    # SECURITY: Validate protocol to prevent schemes like file:// or ssh:// (which can have options injection risks)
    if not repo_url.startswith("https://"):
        logger.error(f"Skipping {repo_name}: Invalid protocol in {repo_url} (only https allowed)")
        return {}

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)

        try:
            # Disable terminal prompts to prevent hanging on authentication requests
            # SECURITY: Use '--' to separate options from positional arguments (the URL)
            # This prevents argument injection if repo_url starts with '-'
            subprocess.run(
                ["git", "clone", "--", repo_url, str(tmpdir)],
                env={**os.environ, "GIT_ASKPASS": "false", "GIT_TERMINAL_PROMPT": "0"},
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Git clone failed for {repo_name}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error processing {repo_name}: {e}")
            return {}

        for theme_file in tmpdir.glob("**/*.yaml"):
            try:
                theme_data = read_kv(theme_file.read_bytes())
                theme_data["repo"] = repo_url
                repo_themes[theme_file.stem] = theme_data
            except Exception as e:
                logger.warning(f"Failed to read theme file {theme_file}: {e}")

    return repo_themes


def process_themes(themes_raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes and validates raw theme data.

    This step ensures that:
    1. The theme has a 'scheme', 'repo', and all 16 required color keys (base00-base0F).
    2. Data is formatted correctly for the Hugo template (colors as a list).

    Args:
        themes_raw: A dictionary of raw theme data extracted from files.

    Returns:
        A filtered and normalized dictionary of themes ready for markdown generation.
        Themes missing required data are excluded.
    """
    processed_themes = {}

    for theme_name, theme_data in themes_raw.items():
        # Copy to avoid modifying original if passed by reference
        data = theme_data.copy()

        scheme = data.get("scheme", theme_name)
        if "scheme" in data:
            data.pop("scheme")

        if "repo" not in data:
            # Should have been added by process_theme_repo, but good to be safe
            continue

        repo = data.pop("repo")

        data["title"] = scheme
        data["summary"] = repo

        colors = []
        skip_theme = False
        for k in COLOR_KEYS:
            if k not in data:
                skip_theme = True
                break
            colors.append(data.pop(k))

        if skip_theme:
            continue

        data["colors"] = colors
        processed_themes[theme_name] = data

    return processed_themes


def generate_markdown_files(themes: Dict[str, Any], output_dir: Path):
    """
    Writes the processed themes to individual Markdown files.

    Existing `theme_*.md` files in the output directory are deleted first to
    ensure that removed themes are not retained (cleanup).

    Args:
        themes: The dictionary of processed themes.
        output_dir: The directory where markdown files will be written.
    """
    logger.info(f"Removing existing theme files in {output_dir}")
    for item in output_dir.glob("theme_*.md"):
        try:
            item.unlink()
        except Exception as e:
            logger.error(f"Failed to delete {item}: {e}")

    logger.info(f"Generating {len(themes)} theme files...")
    for theme_name, theme_data in themes.items():
        file_path = output_dir / f"theme_{theme_name}.md"
        try:
            with file_path.open("w") as f:
                print("---", file=f)
                for k, v in theme_data.items():
                    print(f"{k}: {json.dumps(v)}", file=f)
                print("---", file=f)
        except Exception as e:
            logger.error(f"Failed to write {file_path}: {e}")


def main():
    """
    Main execution flow.
    1. Fetches repo list.
    2. Downloads and extracts themes in parallel.
    3. Processes and filters data.
    4. Generates Markdown files.
    """
    repos = fetch_repo_list(SCHEME_LIST_URL)

    all_raw_themes = {}

    # Process repos in parallel
    with ThreadPoolExecutor() as executor:
        # map returns a generator, iterate to consume
        results = executor.map(lambda item: process_theme_repo(item[0], item[1]), repos.items())

        for repo_themes in results:
            all_raw_themes.update(repo_themes)

    processed_themes = process_themes(all_raw_themes)
    generate_markdown_files(processed_themes, ROOT)
    logger.info("Done.")


if __name__ == "__main__":
    main()
