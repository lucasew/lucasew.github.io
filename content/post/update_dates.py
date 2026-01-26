#!/usr/bin/env python3
"""
Post Date Backfiller

This script automatically populates the `date` field in the frontmatter of Hugo content files
based on the directory naming convention.

Convention:
    The script assumes a directory structure like `content/post/YYYYMMDD-slug/index.md`.
    It extracts the date from the `YYYYMMDD` prefix of the parent directory.

Purpose:
    - To avoid manually typing dates for imported or new posts that follow the naming convention.
    - To ensure consistency between the filesystem structure and the metadata.

Refactoring:
    - Encapsulated logic into `Post` class for better structure and testability.
    - Post class now represents a Page Bundle (directory) and processes all markdown files within it.
"""

import re
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Non-greedy regex to capture frontmatter content between ---
FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


class Post:
    """
    Represents a blog post page bundle (directory) and handles frontmatter manipulation
    for all markdown files within it.
    """

    def __init__(self, bundle_dir: Path, root: Path):
        """
        Args:
            bundle_dir: Path object pointing to the page bundle directory.
            root: The root directory for relative path calculations.
        """
        self.bundle_dir = bundle_dir
        self.root = root

    def extract_date(self) -> Optional[str]:
        """
        Extracts the date from the bundle directory name (YYYYMMDD-slug).
        Returns:
            ISO 8601 date string (YYYY-MM-DDTHH:MM:SS) or None if invalid.
        """
        try:
            # e.g. "content/post/20210228-slug" -> relative "20210228-slug"
            # -> parts[0] "20210228-slug"
            dir_name = self.bundle_dir.relative_to(self.root).parts[0]
            date_part = dir_name.split('-')[0]

            if len(date_part) != 8 or not date_part.isdigit():
                logger.warning(f"{self.bundle_dir}: Could not extract valid date from '{dir_name}'.")
                return None

            y, m, d = date_part[0:4], date_part[4:6], date_part[6:8]
            return f"{y}-{m}-{d}T00:00:00"
        except Exception as e:
            logger.warning(f"{self.bundle_dir}: Error extracting date: {e}")
            return None

    def has_existing_date(self, content: str) -> bool:
        """Checks if the 'date:' key is already present in the frontmatter."""
        match = FRONTMATTER_PATTERN.search(content)
        if not match:
            return False
        frontmatter_content = match.group(1)
        return 'date:' in frontmatter_content

    def inject_date(self, content: str, date_str: str) -> str:
        """
        Injects the date into the frontmatter.
        Returns the modified content.
        """
        match = FRONTMATTER_PATTERN.search(content)
        if not match:
            return content

        frontmatter_body = match.group(1)
        new_frontmatter_body = f"date: {date_str}\n{frontmatter_body}"

        # Replace only the matched group part
        start, end = match.span(1)
        return content[:start] + new_frontmatter_body + content[end:]

    def _process_file(self, file_path: Path, date_str: str):
        """Helper to process a single markdown file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return

        if self.has_existing_date(content):
            return

        logger.info(f"{file_path}: Adding date {date_str}")
        new_content = self.inject_date(content, date_str)

        try:
            file_path.write_text(new_content, encoding='utf-8')
        except Exception as e:
            logger.error(f"{file_path}: Failed to write: {e}")

    def process(self):
        """
        Orchestrates the update process for all markdown files in the bundle.
        """
        date_str = self.extract_date()
        if not date_str:
            return

        # Iterate over all markdown files (e.g., index.md, index.pt.md)
        for file_path in self.bundle_dir.glob("index*.md"):
             self._process_file(file_path, date_str)


def main():
    """
    Main entry point. Scans for page bundles and updates them.
    """
    root = Path(__file__).parent

    # Collect unique page bundle directories
    # We find all index files, then take their parent directories.
    # Using a set to ensure uniqueness.
    bundle_dirs = {
        item.parent
        for item in root.glob('**/index*')
        if item.parent != root
    }

    for bundle_dir in bundle_dirs:
        post = Post(bundle_dir, root)
        post.process()


if __name__ == "__main__":
    main()
