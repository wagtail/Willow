# Releasing

This document describes the process for maintainers to create and publish a new release of Willow.

## Pre-requisites

Before starting a release:

- Ensure the working tree is clean.
- Ensure all intended changes are merged into the release branch.
- Ensure `CHANGELOG.md` is updated for the release.
- Ensure `willow/__init__.py` contains the correct `__version__` number.
- Ensure CI is passing.

Only repository maintainers can create and push release tags.

## 1. Update changelog

The `CHANGELOG.md` file must be updated before creating the release tag.

The release entry must:

- list end-user affecting changes first
- prefix internal-only changes with:
  - `maintenance:`
  - `internal:`

- contain the correct version number
- contain the correct release date

Example:

```markdown
## 1.2.3 - 2026-07-12

- Added support for ...
- Fixed ...
- maintenance: Updated release tooling
- internal: Refactored test infrastructure
```

## 2. Create stable branch (if necessary)

Any non-bugfix release must have a stable branch created for it. The stable branch is used to backport bugfixes to this release since older Wagtail version may rely on an older release-series of Willow.

Example: For a 1.14.0 release, the stable branch should be named `stable/1.14.x` and created from :

`git checkout -b stable/1.14.x`

If you are releasing a bugfix release or are backporting, ensure you do it on the right stable branch. For example, if you are releasing 1.14.1, ensure you backport changes to the `stable/1.14.x` branch.

## 3. Create and push the release tag

Create a tag using the following format:

```text
v[major.minor.bugfix]
```

Examples:

```text
v1.2.3
v2.0.0
```

Push the tag:

```bash
git push origin v1.2.3
```

The tag push triggers the `build-release.yml` GitHub Actions workflow.

## 4. Build release workflow

The `build-release.yml` workflow performs the automated release preparation.

It:

1. Builds the Python distribution files:
   - wheel (`.whl`)
   - source distribution (`.tar.gz`)
2. Runs smoke tests against the generated distributions.
3. Creates GitHub artifact attestations for the generated files.
4. Creates a draft GitHub Release.
5. Uploads the distribution files as release assets.

After the workflow completes, the release remains a draft. You will verify and publish the release in the next step.

## 5. Review the draft release

A maintainer must manually review the draft GitHub Release before publishing.

Draft releases will appear here: https://github.com/wagtail/willow/releases

Verify:

- the release version is correct
- the release notes are correct
- the attached wheel and source distribution files are present

If the release is incorrect:

1. Delete the draft GitHub Release.
2. Fix the issue.
3. Push a new tag (you may replace the previous tag if necessary).
4. Repeat the release process.

Do not modify or replace release assets after review. The release will fail if you do.

## 6. Publish the release

When the release is ready, publish the GitHub Release. Unless you are making a release candidate ("pre-release"), the release should be published as "latest" release.

Published releases are immutable:

- You can't delete or change the tag that corresponds to this release
- You can't replace release assets
- You can't upload additional assets

Publishing the release triggers the `publish.yml` workflow.

## 6. Publish workflow

The `publish.yml` workflow is responsible for publishing artifacts to PyPI.

It:

1. Downloads the assets from the GitHub Release you've just published.
2. Verifies the GitHub attestations created by `build-release.yml`.
3. Ensures the artifacts were produced by the trusted release build workflow.
4. Publishes the verified distributions to PyPI using GitHub Trusted Publishing.

Only artifacts with valid attestations from the release build workflow are published.

## 7. Post-release tasks

After the release has been successfully published:

1. Start a new development section in `CHANGELOG.md`:

```markdown
## 1.14.0 (UNRELEASED)

- Nothing new yet
```

2. Commit the change:

```text
Back to development: v[major.minor].0
```

Example:

```text
Back to development: v1.14.0
```

This marks the start of the next development cycle.

## 8. Profit

You've done it. Maybe share with the world that Willow has a new release if there are cool new things shipping?
