#!/usr/bin/env python3
import json
import logging
import os
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional
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


def read_kv(data: str | bytes) -> Dict[str, str]:
    """Parses key-value pairs from yaml-like content."""
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
    """Fetches the list of scheme repositories."""
    logger.info(f"Fetching scheme list from {url}")
    try:
        with request.urlopen(url) as response:
            return read_kv(response.read())
    except Exception as e:
        logger.error(f"Failed to fetch repo list: {e}")
        return {}


def process_theme_repo(repo_name: str, repo_url: str) -> Dict[str, Any]:
    """Clones a repo and extracts theme data."""
    repo_themes = {}
    logger.info(f"Processing repo: {repo_name} ({repo_url})")

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        # Check if directory exists before removing (TemporaryDirectory creates it)
        # The original code did tmpdir.rmdir(), then passed it to git clone.
        # git clone expects the target directory to be empty or non-existent.
        # TemporaryDirectory creates an empty dir.
        # So we don't need to rmdir, unless git clone refuses to clone into empty dir (it usually accepts empty dir).
        # However, the original code specifically did:
        # tmpdir = Path(tmpdir)
        # tmpdir.rmdir()
        # subprocess.call(['git', 'clone', repos[repo], tmpdir], ...)
        # This implies they wanted git to create the directory.

        # Let's replicate that behavior to be safe.
        try:
            tmpdir.rmdir()
        except OSError:
            pass # Already gone

        try:
            subprocess.run(
                ['git', 'clone', repo_url, str(tmpdir)],
                env={
                    **os.environ,
                    'GIT_ASKPASS': 'false',
                    'GIT_TERMINAL_PROMPT': '0'
                },
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Git clone failed for {repo_name}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error processing {repo_name}: {e}")
            return {}

        for theme_file in tmpdir.glob('**/*.yaml'):
            try:
                theme_data = read_kv(theme_file.read_bytes())
                theme_data['repo'] = repo_url
                repo_themes[theme_file.stem] = theme_data
            except Exception as e:
                logger.warning(f"Failed to read theme file {theme_file}: {e}")

    return repo_themes


def process_themes(themes_raw: Dict[str, Any]) -> Dict[str, Any]:
    """Processes raw theme data, filtering and formatting it."""
    processed_themes = {}

    for theme_name, theme_data in themes_raw.items():
        # Copy to avoid modifying original if passed by reference
        data = theme_data.copy()

        scheme = data.get('scheme', theme_name)
        if 'scheme' in data:
            data.pop('scheme')

        if 'repo' not in data:
            # Should check this, though our logic adds it.
            continue

        repo = data.pop('repo')

        data['title'] = scheme
        data['summary'] = repo

        colors = []
        skip_theme = False
        for k in COLOR_KEYS:
            if k not in data:
                skip_theme = True
                break
            colors.append(data.pop(k))

        if skip_theme:
            continue

        data['colors'] = colors
        processed_themes[theme_name] = data

    return processed_themes


def generate_markdown_files(themes: Dict[str, Any], output_dir: Path):
    """Generates markdown files for each theme."""
    logger.info(f"Removing existing theme files in {output_dir}")
    for item in output_dir.glob('theme_*.md'):
        try:
            item.unlink()
        except Exception as e:
            logger.error(f"Failed to delete {item}: {e}")

    logger.info(f"Generating {len(themes)} theme files...")
    for theme_name, theme_data in themes.items():
        file_path = output_dir / f"theme_{theme_name}.md"
        try:
            with file_path.open('w') as f:
                print('---', file=f)
                for k, v in theme_data.items():
                    print(f"{k}: {json.dumps(v)}", file=f)
                print('---', file=f)
        except Exception as e:
            logger.error(f"Failed to write {file_path}: {e}")


def main():
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
