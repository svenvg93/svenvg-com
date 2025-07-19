---
title: Automating Dependabot for Docker Compose
description: Keep your Docker Compose dependencies secure and up to date by automating Dependabot configuration with a simple Bash script and GitHub Actions.
date: 2025-05-12
draft: false
categories:
  - DevOps
  - CI/CD
tags:
  - dependabot
  - docker
  - github actions
cover: cover.jpg
---

Keeping dependencies up to date is essential for security and maintainability—but manually managing updates across multiple <kbd>docker-compose.yml</kbd> files in a project can be tedious. In this post, I’ll show you a small Bash script I wrote to automate the generation of a <kbd>dependabot.yml</kbd> file. It scans your repo for all Docker Compose files and configures Dependabot to check them for updates monthly. It’s lightweight, efficient, and ensures you never miss a patch. Let’s dive in. We will automate the updating the <kbd>dependabot.yml</kbd> with Github Actions.

## What is dependabot?
[Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates) is a built-in GitHub tool that automatically checks your project dependencies for updates. It can open pull requests when new versions of your dependencies are available - helping you stay secure and up to date with minimal effort. For Docker Compose projects, it monitors container image tags and notifies you when a newer version is published.

## Create generate-dependabot.sh

In the top level of your directory, create a script file to generate <kbd>dependabot.yml</kbd>:

```bash
nano generate-dependabot.sh
```

Paste the following content into the file:

```bash
#!/bin/bash

# Script to generate or update dependabot.yml based on docker-compose.yml files
# Usage: ./generate-dependabot.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Starting dependabot.yml generation..."

mkdir -p .github

tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

# Header
cat > "$tmpfile" <<'YAML'
version: 2
updates:
  - package-ecosystem: "docker-compose"
    directories:
YAML

# Find and sort all docker-compose.yml directories
print_status "Scanning for docker-compose.yml files..."

found_directories=0
while IFS= read -r file; do
    dir=$(dirname "$file" | sed 's|^\./||')
    print_status "Found compose file in: $dir"
    echo "      - \"/$dir\"" >> "$tmpfile"
    ((found_directories++))
done < <(find . -name "docker-compose.yml" -type f | sort)

if [[ $found_directories -eq 0 ]]; then
    print_warning "No docker-compose.yml files found"
    exit 0
fi

# Append the schedule block
cat >> "$tmpfile" <<'YAML'
    schedule:
      interval: "daily"
YAML

# Install if changed
if ! [ -f .github/dependabot.yml ] || ! cmp -s "$tmpfile" .github/dependabot.yml; then
  mv "$tmpfile" .github/dependabot.yml
  print_success "Updated .github/dependabot.yml!"
  print_status "Found $found_directories directories with compose files"
else
  print_status "No changes to .github/dependabot.yml"
  print_status "Found $found_directories directories with compose files"
fi

print_success "Dependabot configuration generation completed!"
```

Make the script executable:

```bash
chmod +x generate-dependabot.sh
```

When you run the script using <kbd>./generate-dependabot.sh</kbd>, it will create (or update) the <kbd>.github/dependabot.yml</kbd> file with a list of all directories containing docker-compose.yml files. Commit this file to your Git repository — Dependabot will then automatically check for updated Docker image versions every month and open a pull request if any updates are found.

You can change the interval to weekly or daily if you prefer.

## Github Actions

To keep your <kbd>dependabot.yml</kbd> up to date automatically, we can use a GitHub Action. Instead of manually running the script every time something is changed , this workflow will run the script above on every push to the repository and creates a pull request when an update is needed. It ensures your configuration always reflects the current state of your project - hands-free.

### Create the workflow file
Create a file at <kbd>.github/workflows/update-dependabot.yml</kbd>:

```shell
name: Update Dependabot Config

on:
  push:
    branches:
      - master
      - main
    paths-ignore:
    - '.github/dependabot.yml'

  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Generate dependabot.yml
        run: ./generate-dependabot.sh

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          commit-message: "chore: update dependabot.yml [automated]"
          title: "Chore: Update dependabot.yml"
          body: |
            This PR was automatically generated by a GitHub Action to update the <kbd>.github/dependabot.yml</kbd> file.
          branch: "chore/update-dependabot-config"
          delete-branch: true
          labels: |
            dependencies
```

Make sure GitHub Actions has permission to create pull requests.

Go to Settings → Actions → General → Workflow permissions, and ensure "Read and write permissions" is selected.
As well as **Allow GitHub Actions to create and approve pull requests** is checked.

You can still manually update the <kbd>dependabot.yml</kbd> file at any time by running the script as described above. This is useful if you want to quickly regenerate the configuration without waiting for GitHub Actions to trigger. Just remember to commit the updated file so Dependabot can pick it up.

With this setup, you can keep your Docker Compose dependencies up to date effortlessly — and ensure your <kbd>dependabot.yml</kbd> file stays in sync as your project evolves. It's a small automation that saves time, prevents surprises, and helps keep your stack secure. Happy automating! 🚀

If you're interested in more GitHub Actions tips, check out my post on [Automating Cloudflare Pages deployments with GitHub Actions](https://svenvg93.github.io/posts/github-actions-cloudflare-pages/).
