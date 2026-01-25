#!/usr/bin/env python3
"""
Backfills the 'date' frontmatter field for Hugo posts based on directory naming conventions.

This script iterates through subdirectories in the script's parent folder, expects a
'YYYYMMDD-slug' naming pattern, and extracts the date. It then inserts this date
into the post's frontmatter if it's missing.

This automates date management for legacy posts or new drafts created without
explicit dates, ensuring Hugo orders them correctly.
"""
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Non-greedy regex to capture frontmatter content between ---
FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

def update_file(file_path: Path, root: Path):
    """
    Updates a single file to inject the date into its frontmatter.

    It performs the following steps:
    1.  Reads the file content.
    2.  Extracts the YAML frontmatter block.
    3.  Checks if 'date:' is already present.
    4.  Extracts the date from the parent directory name (format: YYYYMMDD-...).
    5.  Injects the formatted date (YYYY-MM-DDT00:00:00) into the frontmatter.

    Args:
        file_path (Path): The path to the markdown file to update.
        root (Path): The root directory used to calculate relative paths for date extraction.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return

    match = FRONTMATTER_PATTERN.search(content)
    if not match:
        logger.warning(f"{file_path}: Regex didn't match frontmatter.")
        return

    frontmatter_content = match.group(1)

    if 'date:' in frontmatter_content:
        # Date already present, skip
        return

    # Extract date from directory name
    try:
        # e.g. "20210228-slug" -> "20210228"
        dir_name = file_path.relative_to(root).parts[0]
        date_str = dir_name.split('-')[0]

        if len(date_str) != 8 or not date_str.isdigit():
             logger.warning(f"{file_path}: Could not extract valid date from '{dir_name}'.")
             return

        y, m, d = date_str[0:4], date_str[4:6], date_str[6:8]
        formatted_date = f"{y}-{m}-{d}T00:00:00"
    except Exception as e:
        logger.warning(f"{file_path}: Error extracting date: {e}")
        return

    logger.info(f"{file_path}: Adding date {formatted_date}")

    # Prepend date to frontmatter content
    # Note: Using \n prefix to ensure it starts on a new line if not empty,
    # but strictly we might want it cleanly at the top.
    # The original script did: "\ndate: ...\n" + frontmatter

    new_frontmatter_content = f"date: {formatted_date}\n{frontmatter_content}"

    # Replace only the matched group part to avoid global replace issues
    start, end = match.span(1)
    new_content = content[:start] + new_frontmatter_content + content[end:]

    try:
        file_path.write_text(new_content, encoding='utf-8')
    except Exception as e:
        logger.error(f"{file_path}: Failed to write: {e}")

def main():
    """
    Entry point for the script.

    Finds the script's parent directory and iterates over all `index*` files
    (e.g., `index.md`, `_index.md`) in its subdirectories to apply date updates.
    """
    root = Path(__file__).parent
    # Iterate over all index files in subdirectories
    for item in root.glob('**/index*'):
        update_file(item, root)

if __name__ == "__main__":
    main()
