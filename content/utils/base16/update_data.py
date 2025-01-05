#!/usr/bin/env python3
from pathlib import Path
import os
import tempfile
from urllib import request
import re
import subprocess
import json

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


def read_kv(data):
    LINE_REGEXP = re.compile("^(?P<key>.*): (?P<value>[^#]*)")
    ret = {}
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    for item in data.split('\n'):
        item: str = item.strip()
        item = re.findall(LINE_REGEXP, item)
        if len(item) == 0:
            continue
        item = item[0]
        ret[item[0]] = item[1].strip().strip('"')
    return ret

scheme_repos = request.urlopen("https://raw.githubusercontent.com/chriskempson/base16-schemes-source/refs/heads/main/list.yaml")
repos = read_kv(scheme_repos.read())
themes = {}
for repo in repos.keys():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        tmpdir.rmdir()
        try:
            subprocess.call(['git', 'clone', repos[repo], tmpdir], env={
                **os.environ,
                'GIT_ASKPASS': 'false',
                'GIT_TERMINAL_PROMPT': '0'
            })
        except Exception as e:
            print(e)
        for theme in tmpdir.glob('**/*.yaml'):
            themes[theme.stem] = read_kv(theme.read_bytes())
            themes[theme.stem]['repo'] = repos[repo]
print(themes)

for theme in list(themes.keys()):
    scheme = themes[theme].get('scheme', theme)
    if 'scheme' in themes[theme]:
        scheme = themes[theme].pop('scheme')
    repo = themes[theme].pop('repo')
    themes[theme]['title'] = scheme
    themes[theme]['summary'] = repo
    colors = []
    skip_theme = False
    for k in COLOR_KEYS:
        if k not in themes[theme]:
            skip_theme = True
    if skip_theme:
        themes.pop(theme)
        continue
    for k in COLOR_KEYS:
        colors.append(themes[theme].pop(k))
    themes[theme]['colors'] = colors
    # themes[theme]['type'] = 'utils_base16'

for item in ROOT.glob('theme_*.md'):
    item.unlink()

for theme in themes.keys():
    file = ROOT / f"theme_{theme}.md"
    with file.open('w') as f:
        print('---', file=f)
        for (k, v) in themes[theme].items():
            print(f"{k}: {json.dumps(v)}", file=f)
        print('---', file=f)
