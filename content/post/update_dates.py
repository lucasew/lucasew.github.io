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
"""

import re
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class Post:
    """
    Represents a blog post file and handles frontmatter manipulation.
    """
    # Non-greedy regex to capture frontmatter content between ---
    FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

    def __init__(self, path: Path, root: Path):
        """
        Args:
            path: Path object pointing to the markdown file.
            root: The root directory for relative path calculations.
        """
        self.path = path
        self.root = root

    def read_content(self) -> str:
        """Reads the file content."""
        return self.path.read_text(encoding='utf-8')

    def save_content(self, content: str):
        """Writes content back to the file."""
        self.path.write_text(content, encoding='utf-8')

    def extract_date(self) -> Optional[str]:
        """
        Extracts the date from the parent directory name (YYYYMMDD-slug).
        Returns:
            ISO 8601 date string (YYYY-MM-DDTHH:MM:SS) or None if invalid.
        """
        try:
            # e.g. "content/post/20210228-slug/index.md" -> relative "20210228-slug/index.md"
            # -> parts[0] "20210228-slug"
            dir_name = self.path.relative_to(self.root).parts[0]
            date_part = dir_name.split('-')[0]

            if len(date_part) != 8 or not date_part.isdigit():
                logger.warning(f"{self.path}: Could not extract valid date from '{dir_name}'.")
                return None

            y, m, d = date_part[0:4], date_part[4:6], date_part[6:8]
            return f"{y}-{m}-{d}T00:00:00"
        except Exception as e:
            logger.warning(f"{self.path}: Error extracting date: {e}")
            return None

    def has_existing_date(self, content: str) -> bool:
        """Checks if the 'date:' key is already present in the frontmatter."""
        match = self.FRONTMATTER_PATTERN.search(content)
        if not match:
            return False
        frontmatter_content = match.group(1)
        return 'date:' in frontmatter_content

    def inject_date(self, content: str, date_str: str) -> str:
        """
        Injects the date into the frontmatter.
        Returns the modified content.
        """
        match = self.FRONTMATTER_PATTERN.search(content)
        if not match:
            return content

        frontmatter_body = match.group(1)
        new_frontmatter_body = f"date: {date_str}\n{frontmatter_body}"

        # Replace only the matched group part
        start, end = match.span(1)
        return content[:start] + new_frontmatter_body + content[end:]

    def process(self):
        """
        Orchestrates the update process for this post.
        """
        try:
            content = self.read_content()
        except Exception as e:
            logger.error(f"Failed to read {self.path}: {e}")
            return

        if self.has_existing_date(content):
            return

        date_str = self.extract_date()
        if not date_str:
            return

        logger.info(f"{self.path}: Adding date {date_str}")
        new_content = self.inject_date(content, date_str)

        try:
            self.save_content(new_content)
        except Exception as e:
            logger.error(f"{self.path}: Failed to write: {e}")


def main():
    """
    Main entry point. Scans for index files in subdirectories and updates them.
    """
    root = Path(__file__).parent
    # Iterate over all index files in subdirectories
    for item in root.glob('**/index*'):
        # Skip the root index files if any match the pattern, although glob '**/index*' usually picks them up
        # We generally expect content/post/SLUG/index.md
        if item.parent == root:
            continue

        post = Post(item, root)
        post.process()


if __name__ == "__main__":
    main()
