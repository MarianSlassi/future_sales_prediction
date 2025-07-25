# CI/CD Workflow Documentation

This document describes the automated workflows for this project, located in `.github/workflows/publish.yml`.

## Jobs Overview

### 1. pre-commit
- **Runs on:** Every push to any branch and every pull request to any branch (i.e., when you push commits to GitHub or open/update a pull request).
- **Purpose:** Runs all pre-commit hooks to check code quality and formatting before code is merged or released.
- **What it does:**
  - Checks for and removes trailing whitespace from all files.
  - Ensures every file ends with a newline (end-of-file fixer).
  - Validates YAML files for syntax errors.
  - Prevents large files from being accidentally committed.
  - Runs any additional hooks you configure in `.pre-commit-config.yaml`.
- **How it works:**
  - Checks out the code.
  - Sets up Python 3.11.
  - Installs pre-commit.
  - Runs all pre-commit hooks on all files using `pre-commit run --all-files`.
- **Custom actions:**
  - You can add custom hooks in `.pre-commit-config.yaml` under the `repo: local` section. For example, you could add a hook to run `bump2version patch --allow-dirty` or any other script. These will be executed as part of the pre-commit job if configured.

### 2. build-and-publish
- **Runs on:** When a GitHub Release is published (via the Releases tab or API).
- **Purpose:** Builds the Python package and uploads it to TestPyPI.
- **Steps:**
  - Checks out the code.
  - Sets up Python 3.11.
  - Cleans the `dist` directory.
  - Installs build tools (`build`, `twine`).
  - Builds the package.
  - Publishes the package to TestPyPI using credentials stored in repository secrets.

## How to Use

### Pre-commit Hooks
- Pre-commit hooks are run automatically on every push and pull request to GitHub.
- To run them locally, install pre-commit and run:
  ```sh
  pre-commit run --all-files
  ```
- You can customize or add hooks in `.pre-commit-config.yaml`.

### Publishing a Release
- To publish a new package version:
  1. Create and publish a new release on GitHub (via the Releases tab).
  2. The `build-and-publish` job will run automatically and upload the package to TestPyPI.

### Required Secrets
- `TEST_PYPI_API_TOKEN`: API token for authenticating with TestPyPI. Add this in your repository settings under Settings > Secrets and variables > Actions.

## File Locations
- Workflow file: `.github/workflows/publish.yml`
- Pre-commit config: `.pre-commit-config.yaml`
- This documentation: `docs/ci-cd.md`

## Notes
- Each job runs in a separate environment and must set up its own dependencies.
- The `pre-commit` job helps maintain code quality by enforcing formatting, syntax, and file size rules before code is merged or released.
- The `build-and-publish` job ensures only published releases are uploaded to TestPyPI.
