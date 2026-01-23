#!/usr/bin/env python3
import json
import os
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib import request

ROOT = Path(__file__).parent
SCHEME_LIST_URL = "https://raw.githubusercontent.com/chriskempson/base16-schemes-source/refs/heads/main/list.yaml"
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


def read_kv(data: str | bytes) -> dict[str, str]:
    line_regexp = re.compile(r"^(?P<key>.*): (?P<value>[^#]*)")
    ret = {}
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    for item in data.split('\n'):
        item_str: str = item.strip()
        matches = re.findall(line_regexp, item_str)
        if not matches:
            continue
        key, value = matches[0]
        ret[key] = value.strip().strip('"')
    return ret


def handle_repo(repo_entry: tuple[str, str]) -> dict:
    repo_name, repo_url = repo_entry
    repo_themes = {}
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Remove the directory so git clone can create it fresh
        tmp_path.rmdir()

        try:
            subprocess.call(['git', 'clone', repo_url, str(tmp_path)], env={
                **os.environ,
                'GIT_ASKPASS': 'false',
                'GIT_TERMINAL_PROMPT': '0'
            }, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error cloning {repo_name}: {e}")

        if not tmp_path.exists():
             return {}

        for theme in tmp_path.glob('**/*.yaml'):
            try:
                content = theme.read_bytes()
                parsed = read_kv(content)
                parsed['repo'] = repo_url
                repo_themes[theme.stem] = parsed
            except Exception as e:
                print(f"Error reading theme {theme}: {e}")

    return repo_themes


def main():
    try:
        scheme_repos_resp = request.urlopen(SCHEME_LIST_URL)
        repos = read_kv(scheme_repos_resp.read())
    except Exception as e:
        print(f"Failed to fetch scheme list: {e}")
        return

    themes = {}

    with ThreadPoolExecutor() as tp:
        for repo_theme in tp.map(handle_repo, repos.items()):
            for theme_name, theme_value in repo_theme.items():
                themes[theme_name] = theme_value

    for theme in list(themes.keys()):
        theme_data = themes[theme]
        scheme = theme_data.get('scheme', theme)
        if 'scheme' in theme_data:
            scheme = theme_data.pop('scheme')

        repo = theme_data.pop('repo', '')

        theme_data['title'] = scheme
        theme_data['summary'] = repo

        colors = []
        skip_theme = False
        for k in COLOR_KEYS:
            if k not in theme_data:
                skip_theme = True
                break

        if skip_theme:
            themes.pop(theme)
            continue

        for k in COLOR_KEYS:
            colors.append(theme_data.pop(k))
        theme_data['colors'] = colors

    # Clean up old files
    for item in ROOT.glob('theme_*.md'):
        item.unlink()

    # Write new files
    for theme, data in themes.items():
        file = ROOT / f"theme_{theme}.md"
        with file.open('w') as f:
            print('---', file=f)
            for k, v in data.items():
                print(f"{k}: {json.dumps(v)}", file=f)
            print('---', file=f)


if __name__ == "__main__":
    main()
