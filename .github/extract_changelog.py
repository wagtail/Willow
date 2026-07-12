#!/usr/bin/env python3
import re
import sys


def extract_changelog(version):
    with open("CHANGELOG.md") as f:
        changelog = f.read()

    # Strip any leading "v" from the version string for matching.
    version = version.lstrip("v")

    # Use a regular expression to find the section for the given version.
    # The section appear as ## [0.9.0] followed by the content until the next ## or the end of the file.
    # Expected example output:
    # ## 0.8.0 - 2026-01-09

    # - Add support for Python 3.14 (Storm Heg)
    # - Drop support for Python 3.9 (Storm Heg)
    # - The minimum required pillow-heif version is now 1.0.0 (Storm Heg)
    # - Add support for Pillow 12 and beyond, removed hard upper bound (Storm
    # Heg)

    pattern = rf"## {re.escape(version)}.*?(?=## |\Z)"
    match = re.search(pattern, changelog, re.DOTALL)

    if match:
        return match.group(0).strip()
    else:
        sys.stderr.write(f"Version {version} not found in CHANGELOG.md\n")
        sys.exit(1)


def check_not_unreleased(changelog):
    # The first line cannot have "Unreleased" in it! That means the date is missing and the changelog is not ready for release.
    first_line = changelog.splitlines()[0]
    if "unreleased" in first_line.lower():
        sys.stderr.write(
            "Changelog is not ready for release, it contains 'Unreleased' in the first line. \n"
            + first_line
            + "\n"
        )
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python extract_changelog.py <version>\n")
        sys.stderr.write("Example: python extract_changelog.py v0.9.0\n")
        sys.exit(1)

    version = sys.argv[1]
    changelog = extract_changelog(version)
    check_not_unreleased(changelog)
    # Strip the first line, GitHub releases interface has their own title and
    # date so we don't need the one from the changelog.
    changelog = "\n".join(changelog.splitlines()[1:]).strip()
    sys.stdout.write(changelog + "\n")
