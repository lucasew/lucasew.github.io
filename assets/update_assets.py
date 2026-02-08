#!/usr/bin/env python3
"""
Asset Updater

Consolidates the downloading of external static assets into a single, data-driven script.
Replaces multiple bash scripts to improve maintainability and centralize configuration.

Design Pattern: Command / Table-Driven
Principle: Single Responsibility Principle (SRP), Don't Repeat Yourself (DRY)
"""

import logging
import urllib.request
import urllib.error
from pathlib import Path
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent


@dataclass
class Asset:
    filename: str
    url: str


ASSETS = [
    Asset("analytics.js", "https://analytics.app.lew.tec.br/script.js"),
    Asset("htmx.js", "https://unpkg.com/htmx.org@2.0.4"),
    Asset(
        "sentry.js", "https://js.sentry-cdn.com/df310b7f294d8efd87f5d28526f5189d.min.js"
    ),
]


def update_asset(asset: Asset):
    target_path = ROOT / asset.filename
    logger.info(f"Updating {asset.filename} from {asset.url}")
    try:
        # Use a timeout to prevent hanging indefinitely
        with urllib.request.urlopen(asset.url, timeout=30) as response:
            content = response.read()
            target_path.write_bytes(content)
            logger.info(f"Successfully updated {asset.filename}")
    except urllib.error.URLError as e:
        logger.error(f"Failed to download {asset.filename}: {e}")
    except Exception as e:
        logger.error(f"Error processing {asset.filename}: {e}")


def main():
    logger.info("Starting asset update...")
    for asset in ASSETS:
        update_asset(asset)
    logger.info("Asset update complete.")


if __name__ == "__main__":
    main()
