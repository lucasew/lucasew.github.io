#!/usr/bin/env python3
"""
Asset Updater

This script automates the process of fetching external JavaScript assets.
It replaces multiple individual shell scripts, centralizing the configuration
and execution logic.

Assets managed:
- HTMX (htmx.js)
- Sentry (sentry.js)
- Analytics (analytics.js)
"""

import logging
import urllib.request
import sys
from pathlib import Path
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent

# Configuration: Filename -> URL
ASSETS: Dict[str, str] = {
    "htmx.js": "https://unpkg.com/htmx.org@2.0.4",
    "sentry.js": "https://js.sentry-cdn.com/df310b7f294d8efd87f5d28526f5189d.min.js",
    "analytics.js": "https://analytics.app.lew.tec.br/script.js",
}

def download_file(url: str, dest_path: Path, timeout: int = 10) -> bool:
    """
    Downloads a file from a URL to a destination path with a timeout.

    Args:
        url: The URL to download from.
        dest_path: The local path to save the file to.
        timeout: Timeout in seconds for the request.

    Returns:
        True if successful, False otherwise.
    """
    logger.info(f"Downloading {url} -> {dest_path.name}...")
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = response.read()
            dest_path.write_bytes(data)
            logger.info(f"Successfully updated {dest_path.name}")
            return True
    except Exception as e:
        logger.error(f"Failed to download {dest_path.name}: {e}")
        return False

def main():
    """
    Main execution flow.
    Iterates through the ASSETS configuration and downloads each file.
    Exits with status 1 if any download fails.
    """
    failed = False
    for filename, url in ASSETS.items():
        dest_path = ROOT / filename
        if not download_file(url, dest_path):
            failed = True

    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
