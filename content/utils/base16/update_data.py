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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List
from urllib import request

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent
COLOR_KEYS = [
    'base00',
    'base01',
    'base02',
    'base03',
    'base04',
    'base05',
    'base06',
    'base07',
    'base08',
    'base09',
    'base0A',
    'base0B',
    'base0C',
    'base0D',
    'base0E',
    'base0F',
]
SCHEME_LIST_URL = "https://raw.githubusercontent.com/chriskempson/base16-schemes-source/refs/heads/main/list.yaml"


@dataclass
class Base16Theme:
    """
    Represents a Base16 theme, encapsulating its data validation and normalization.

    Attributes:
        name: The name of the theme (usually the filename stem).
        repo_url: The URL of the repository where the theme was found.
        raw_data: The raw dictionary parsed from the theme's YAML file.
    """
    name: str
    repo_url: str
    raw_data: Dict[str, str]
    normalized_data: Dict[str, Any] = field(default_factory=dict, init=False)

    def is_valid(self) -> bool:
        """
        Checks if the theme contains all required color keys (base00-base0F).
        """
        return all(key in self.raw_data for key in COLOR_KEYS)

    def normalize(self) -> None:
        """
        Normalizes the raw data into a format suitable for Hugo templates.
        Populates self.normalized_data.
        """
        data = self.raw_data.copy()

        # Extract metadata
        scheme = data.pop('scheme', self.name)
        author = data.pop('author', '')

        self.normalized_data = {
            'title': scheme,
            'summary': self.repo_url,
            'author': author
        }

        # Extract colors in order
        colors = []
        for k in COLOR_KEYS:
            if k in data:
                colors.append(data.pop(k))

        self.normalized_data['colors'] = colors

        # Keep any remaining keys if needed, though usually we just want the colors
        # self.normalized_data.update(data)

    def save(self, output_dir: Path) -> None:
        """
        Writes the normalized theme data to a Markdown file.
        """
        if not self.normalized_data:
            self.normalize()

        file_path = output_dir / f"theme_{self.name}.md"
        try:
            with file_path.open('w', encoding='utf-8') as f:
                print('---', file=f)
                for k, v in self.normalized_data.items():
                    print(f"{k}: {json.dumps(v)}", file=f)
                print('---', file=f)
        except Exception as e:
            logger.error(f"Failed to write {file_path}: {e}")


def read_kv(data: str | bytes) -> Dict[str, str]:
    """
    Parses key-value pairs from simple YAML-like content.

    Args:
        data: The content to parse, as a string or bytes.

    Returns:
        A dictionary containing the parsed key-value pairs.
    """
    line_regexp = re.compile(r"^(?P<key>.*): (?P<value>[^#]*)")
    ret = {}
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    for item in data.split('\n'):
        item_str = item.strip()
        match = line_regexp.match(item_str)
        if not match:
            continue
        key = match.group('key').strip()
        value = match.group('value').strip().strip('"')
        ret[key] = value
    return ret


def fetch_repo_list(url: str) -> Dict[str, str]:
    """
    Fetches the authoritative list of base16 scheme repositories.

    Args:
        url: The URL of the scheme list YAML file.

    Returns:
        A dictionary mapping repo names to their Git URLs.
    """
    logger.info(f"Fetching scheme list from {url}")
    try:
        with request.urlopen(url, timeout=10) as response:
            return read_kv(response.read())
    except Exception as e:
        logger.error(f"Failed to fetch repo list: {e}")
        return {}


def process_theme_repo(repo_name: str, repo_url: str) -> List[Base16Theme]:
    """
    Clones a single theme repository and extracts all valid theme definitions.

    Args:
        repo_name: The name of the repository (for logging).
        repo_url: The git URL to clone.

    Returns:
        A list of Base16Theme objects extracted from the repository.
    """
    themes: List[Base16Theme] = []
    logger.info(f"Processing repo: {repo_name} ({repo_url})")

    # SECURITY: Validate protocol to prevent schemes like file:// or ssh://
    if not repo_url.startswith("https://"):
        logger.error(f"Skipping {repo_name}: Invalid protocol in {repo_url} (only https allowed)")
        return []

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)

        try:
            # Disable terminal prompts and set timeout
            subprocess.run(
                ['git', 'clone', '--', repo_url, str(tmpdir)],
                env={
                    **os.environ,
                    'GIT_ASKPASS': 'false',
                    'GIT_TERMINAL_PROMPT': '0'
                },
                check=True,
                capture_output=True,
                timeout=30
            )
        except subprocess.TimeoutExpired:
            logger.error(f"Git clone timed out for {repo_name}")
            return []
        except subprocess.CalledProcessError as e:
            logger.error(f"Git clone failed for {repo_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing {repo_name}: {e}")
            return []

        for theme_file in tmpdir.glob('**/*.yaml'):
            try:
                theme_data = read_kv(theme_file.read_bytes())
                theme = Base16Theme(
                    name=theme_file.stem,
                    repo_url=repo_url,
                    raw_data=theme_data
                )
                if theme.is_valid():
                    theme.normalize()
                    themes.append(theme)
            except Exception as e:
                logger.warning(f"Failed to read/parse theme file {theme_file}: {e}")

    return themes


def clean_existing_themes(output_dir: Path):
    """Removes existing theme files in the output directory."""
    logger.info(f"Removing existing theme files in {output_dir}")
    for item in output_dir.glob('theme_*.md'):
        try:
            item.unlink()
        except Exception as e:
            logger.error(f"Failed to delete {item}: {e}")


def main():
    """
    Main execution flow.
    """
    repos = fetch_repo_list(SCHEME_LIST_URL)

    all_themes: List[Base16Theme] = []

    # Process repos in parallel
    with ThreadPoolExecutor() as executor:
        # map returns a generator, iterate to consume
        results = executor.map(lambda item: process_theme_repo(item[0], item[1]), repos.items())

        for repo_themes in results:
            all_themes.extend(repo_themes)

    clean_existing_themes(ROOT)

    logger.info(f"Generating {len(all_themes)} theme files...")
    for theme in all_themes:
        theme.save(ROOT)

    logger.info("Done.")


if __name__ == "__main__":
    main()
