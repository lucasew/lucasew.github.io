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
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent

@dataclass
class Asset:
    """
    Represents an external asset to be downloaded, mapping a local filename to a remote URL.

    Attributes:
        filename: The local filename to save the asset as.
        url: The remote URL to download the asset from.
    """
    filename: str
    url: str

ASSETS = [
    Asset("analytics.js", "https://analytics.app.lew.tec.br/script.js"),
    Asset("htmx.js", "https://unpkg.com/htmx.org@2.0.4"),
    Asset("sentry.js", "https://js.sentry-cdn.com/df310b7f294d8efd87f5d28526f5189d.min.js"),
]

def update_asset(asset: Asset):
    """
    Downloads a single asset from its URL to the local filesystem.

    Handles network timeouts (30s) and logs errors without raising, ensuring failure
    of one asset does not stop the entire update process.

    Args:
        asset: The Asset object containing the filename and URL.
    """
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
    """
    Orchestrates the update process for all defined assets.
    """
    logger.info("Starting asset update...")
    for asset in ASSETS:
        update_asset(asset)
    logger.info("Asset update complete.")

if __name__ == "__main__":
    main()
