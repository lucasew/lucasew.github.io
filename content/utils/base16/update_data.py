#!/usr/bin/env python3
from pathlib import Path
import os
import tempfile
from urllib import request
import re
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor

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

LINE_REGEXP = re.compile("^(?P<key>.*): (?P<value>[^#]*)")

def read_kv(data):
    ret = {}
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    for item in data.split('\n'):
        item: str = item.strip()
        matches = re.findall(LINE_REGEXP, item)
        if len(matches) == 0:
            continue
        key, value = matches[0]
        ret[key] = value.strip().strip('"')
    return ret

def handle_repo(repo_url):
    repo_themes = {}
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        try:
            subprocess.run(
                ['git', 'clone', repo_url, str(tmpdir_path)],
                env={
                    **os.environ,
                    'GIT_ASKPASS': 'false',
                    'GIT_TERMINAL_PROMPT': '0'
                },
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error cloning {repo_url}: {e}")
            return repo_themes
        except Exception as e:
            print(f"Unexpected error handling {repo_url}: {e}")
            return repo_themes

        for theme in tmpdir_path.glob('**/*.yaml'):
            try:
                repo_themes[theme.stem] = read_kv(theme.read_bytes())
                repo_themes[theme.stem]['repo'] = repo_url
            except Exception as e:
                print(f"Error reading theme {theme}: {e}")
    return repo_themes

def main():
    try:
        scheme_repos = request.urlopen("https://raw.githubusercontent.com/chriskempson/base16-schemes-source/refs/heads/main/list.yaml")
        repos = read_kv(scheme_repos.read())
    except Exception as e:
        print(f"Failed to fetch repos list: {e}")
        return

    themes = {}

    with ThreadPoolExecutor() as tp:
        # map returns an iterator of results
        for repo_themes in tp.map(handle_repo, repos.values()):
            for theme_name, theme_value in repo_themes.items():
                themes[theme_name] = theme_value

    for theme in list(themes.keys()):
        scheme = themes[theme].get('scheme', theme)
        if 'scheme' in themes[theme]:
            scheme = themes[theme].pop('scheme')

        # 'repo' is guaranteed to be there if handle_repo worked, but safe get
        repo = themes[theme].pop('repo', '')

        themes[theme]['title'] = scheme
        themes[theme]['summary'] = repo
        colors = []
        skip_theme = False
        for k in COLOR_KEYS:
            if k not in themes[theme]:
                skip_theme = True
                break # Added break for efficiency
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

if __name__ == "__main__":
    main()
