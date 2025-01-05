#!/usr/bin/env python3
from pathlib import Path
import re
regex = r"^---\n(.*)\n---"

ROOT = Path(__file__).parent
for item in ROOT.glob('**/index*'):
    item_text = item.read_text()
    if 'date:' in item_text:
        continue
    matches = re.findall(regex, item_text, re.DOTALL)
    if len(matches) == 0:
        continue
    frontmatter = matches[0]
    date = item.relative_to(ROOT).parts[0].split('-')[0]
    y, m, d = date[0:4], date[4:6], date[6:8]

    new_frontmatter = f"\ndate: {y}-{m}-{d}T00:00:00-00:00\n"
    new_frontmatter += frontmatter

    item.write_text(item_text.replace(frontmatter, new_frontmatter))
