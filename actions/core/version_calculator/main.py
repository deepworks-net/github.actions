# version_calculator.py
# Reusable script for version calculation

import subprocess
import re
import sys

def setup_git():
    """Configure git to trust the workspace."""
    try:
        subprocess.check_output(['git', 'config', '--global', '--add', 'safe.directory', '/github/workspace'], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error configuring git: {e}")
        sys.exit(1)

def get_latest_tag():
    """Retrieve the latest version tag."""
    try:
        output = subprocess.check_output(['git', 'tag', '-l', '--sort=-v:refname'], text=True).strip()
        return output.splitlines()[0] if output else 'v0.1.0'  # Default to v0.1.0 if no tags
    except subprocess.CalledProcessError as e:
        print(f"Error fetching tags: {e}")
        sys.exit(1)

def get_commit_count_since_tag(tag):
    """Count commits since the latest tag."""
    try:
        if tag == 'v0.1.0':  # If using default tag, return 0
            return 0
        else:
            output = subprocess.check_output(['git', 'rev-list', f'{tag}..HEAD', '--count'], text=True).strip()
            return int(output)
    except subprocess.CalledProcessError as e:
        print(f"Error counting commits: {e}")
        sys.exit(1)

def calculate_next_version(latest_tag, version_prefix='v'):
    """Calculate the next version based on the latest tag."""
    pattern = f'{version_prefix}(\\d+)\\.(\\d+)\\.(\\d+)'
    match = re.match(pattern, latest_tag)
    if not match:
        print(f"Invalid version format: {latest_tag}")
        sys.exit(1)

    # If we're using default version, don't add commits
    if latest_tag == f"{version_prefix}0.1.0":
        return latest_tag

    major, minor, patch = map(int, match.groups())
    commit_count = get_commit_count_since_tag(latest_tag)
    next_patch = patch + commit_count
    return f"{version_prefix}{major}.{minor}.{next_patch}"

def main():
    setup_git()  # Configure git before running commands
    latest_tag = get_latest_tag()
    print(f"Latest tag: {latest_tag}")

    next_version = calculate_next_version(latest_tag)
    print(f"Next version: {next_version}")

    # Output the next version for GitHub Actions
    print(f"::set-output name=next_version::{next_version}")

if __name__ == "__main__":
    main()