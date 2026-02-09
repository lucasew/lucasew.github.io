"""
Shared utilities for Python scripts in this repository.
"""
import logging
import urllib.request
import urllib.error
import subprocess
import os

def setup_logging():
    """Configures basic logging for scripts."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def report_error(msg, exc=None):
    """
    Centralized error reporting.
    Logs the error message. If an exception is provided, logs the traceback.
    """
    if exc:
        logging.error(f"{msg}: {exc}", exc_info=True)
    else:
        logging.error(msg)

def fetch_url_content(url: str, timeout: int = 30) -> bytes:
    """
    Fetches content from a URL with a timeout.
    Returns bytes content.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read()
    except Exception as e:
        report_error(f"Failed to fetch {url}", e)
        raise

def run_git_clone(url: str, target_dir: str, timeout: int = 60):
    """
    Runs git clone with security checks (disabling prompts).
    """
    try:
        subprocess.run(
            ['git', 'clone', '--', url, str(target_dir)],
            env={
                **os.environ,
                'GIT_ASKPASS': 'false',
                'GIT_TERMINAL_PROMPT': '0'
            },
            check=True,
            capture_output=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        report_error(f"Git clone timed out for {url}")
        raise
    except subprocess.CalledProcessError as e:
        report_error(f"Git clone failed for {url}", e)
        raise
    except Exception as e:
        report_error(f"Error cloning {url}", e)
        raise
