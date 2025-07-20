---
title: Deploying a Hugo Site with Cloudflare Workers
description: Deploy your Hugo Website to Cloudflare with Github Actouns
date: 2025-07-20
draft: false
categories:
  - DevOps
  - CI/CD
tags:
  - github actions
  - hugo
  - cloudflare workers
cover: cover.jpg
---

I recently migrated my blog from Jekyll to Hugo — more on that soon. As part of the migration, I needed to set up deployments to Cloudflare. I typically use Cloudflare Pages, but when I went to configure it, I was met with a notice recommending Cloudflare Workers for new projects.

While Cloudflare hasn’t explicitly stated the future of Pages, it’s clear that the focus and innovation are shifting toward Workers.

In this post, I’ll walk you through how to set up your Hugo site for deployment using Cloudflare Workers, and how to customize the build process triggered by GitHub Actions.

## Add Worker Files to Your Repository

Unfortunately, Cloudflare Workers doesn’t provide a plug-and-play template for deploying Hugo sites. To make the deployment work, we need to add two custom files:

### Build Script

This script handles building your Hugo site with the desired versions of Sass and Hugo.

What it does:
- Installs Dart Sass v1.89.2 and Hugo v0.148.0
- Sets the timezone
- Adds binaries to the PATH
- Verifies installed versions of Sass, Go, Hugo, and Node.js
- Fetches Git history and submodules (for Hugo GitInfo)
- Builds the site using --gc and --minify

```bash {filename="buidl.sh"}
#!/usr/bin/env bash

#------------------------------------------------------------------------------
# @file
# Builds a Hugo site hosted on a Cloudflare Worker.
#
# The Cloudflare Worker build image already includes Go, Hugo (an old version),
# and Node js. Set the desired Dart Sass and Hugo versions below.
#
# The Cloudflare Worker automatically installs Node.js dependencies.
#------------------------------------------------------------------------------

main() {

  DART_SASS_VERSION=1.89.2
  HUGO_VERSION=0.148.0

  export TZ=Europe/Amsterdam

  # Install Dart Sass
  echo "Installing Dart Sass v${DART_SASS_VERSION}..."
  curl -LJO "https://github.com/sass/dart-sass/releases/download/${DART_SASS_VERSION}/dart-sass-${DART_SASS_VERSION}-linux-x64.tar.gz"
  tar -xf "dart-sass-${DART_SASS_VERSION}-linux-x64.tar.gz"
  cp -r dart-sass/ /opt/buildhome
  rm -rf dart-sass*

  # Install Hugo
  echo "Installing Hugo v${HUGO_VERSION}..."
  curl -LJO https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz
  tar -xf "hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz"
  cp hugo /opt/buildhome
  rm LICENSE README.md hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz

  # Set PATH
  echo "Setting the PATH environment variable..."
  export PATH=/opt/buildhome:/opt/buildhome/dart-sass:$PATH

  # Verify installed versions
  echo "Verifying installations..."
  echo Dart Sass: "$(sass --version)"
  echo Go: "$(go version)"
  echo Hugo: "$(hugo version)"
  echo Node.js: "$(node --version)"

  # https://gohugo.io/methods/page/gitinfo/#hosting-considerations
  git fetch --recurse-submodules --unshallow

  # https://github.com/gohugoio/hugo/issues/9810
  git config core.quotepath false

  # Build the site.
  hugo --gc --minify

}

set -euo pipefail
main "$@"
```
### Cloudflare Worker Configuration

This file tells Cloudflare how to build and serve your site.

```toml {filename="wrangler.toml"}
# Configure Cloudflare Worker

name = 'svenvg-com'
compatibility_date = "2025-07-20"

[build]
command = "./build.sh"

[assets]
directory = "./public"
not_found_handling = "404-page"
```
**Note:** Replace the name value with your own domain or project name.

Commit the files to your Git repro.

## Set Up Cloudflare Worker

Next, configure your Cloudflare Worker to deploy the site:

1. Open your Cloudflare Dashboard
2. Navigate to Compute (Workers) → Workers & Pages
3. Click Get Started under Import a Repository
4. Select Connect to Git and link your GitHub account if prompted
5. Choose the repository you committed the files to
6. Enter a Project name of your choice
7. Leave the remaining settings at their defaults and click Create and Deploy

Cloudflare will now build and deploy your website. After a few minutes, you can preview it at the automatically generated **.workers.dev* URL.

### Custom Domain

The default *.workers.dev URL isn’t ideal for branding or memorability, so let’s add your own custom domain:
1. Open your Worker project and navigate to the Settings tab
2. Under Domains & Routes, click + Add
3. Select Custom domain
4. Enter your domain name (e.g. example.com)
5. Click Add domain to complete the setup

Cloudflare will setup  your domain and configure the DNS. It might take a few minutes before the domain name works. 

## Github Actions

Cloudflare monitors your repository for changes and automatically rebuilds your site when updates are pushed.
Alternatively, you can use GitHub Actions to trigger builds manually or on your own schedule — giving you more control over the deployment process.

### Cloudflare API Token 

To authenticate GitHub Actions with Cloudflare, you’ll need to generate an API token:
1. Go to the Cloudflare API Tokens page and log in.
2. Click Create Token.
3. Choose the Edit Cloudflare Workers template.
4. Customize the token:
    - Name it something like Deploy Hugo Blog
    - Under Zone Resources, select the appropriate domain
    - Under Account Resources, select your Cloudflare account
5. Click Continue to summary and review the permissions
6. Click Create Token to generate it
7. Copy and save the token securely — you’ll need it later for GitHub Secrets

### Cloudflare Account ID

1. In the Cloudflare dashboard, go to your Account Home
2. Click the three-dot menu next to your account name
3. Click Copy Account ID
4. Save this ID securely — it will also be added to GitHub Secrets

### Github Secrets
To securely store the API token and account ID:
1. Navigate to your GitHub repository
2. Go to Settings → Secrets and variables → Actions
3. Click New repository secret
5. Add the following secrets:

**CLOUDFLARE_ACCOUNT_ID**
- Name: CLOUDFLARE_ACCOUNT_ID
- Value: (paste your account ID)

**CLOUDFLARE_API_TOKEN**
- Name: CLOUDFLARE_API_TOKEN
- Value: (paste your API token)

These secrets are encrypted and will only be used securely by GitHub Actions during deployment.

### Workflow

With all the access methods configured, the next step is to create the workflow file.
Create a file named <kbd>deploy.yml</kbd> inside the <kbd>.github/workflows</kbd> directory of your repository.

```yaml {filename="deploy.yml"}
name: Deploy to Cloudflare
on:
  push:
    branches:
      - main
    paths-ignore:
      - '.github/**'
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v4
      - name: Build & Deploy Worker
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```
**Note:** Make sure to update the branch name to match the default branch of your repository (e.g., main or master).

On every push to the configured branch, this action will trigger a new build and deployment via Cloudflare.

### Disable Cloudflare’s Automatic Builds

Since GitHub Actions now handles deployments, we can disable Cloudflare’s automatic builds to prevent duplicate deployments.
1. Open your Worker project and go to the Settings tab
2. Scroll to the Build section and edit the Build watch paths
3. Set the following values:
    - Include paths: []
    - Exclude paths: *
4. Click Update

This effectively disables Cloudflare’s automatic builds by including nothing and excluding everything.

By combining Hugo, GitHub Actions, and Cloudflare Workers, you now have a fast, reliable, and customizable static site deployment pipeline. With your own build script and GitHub-managed workflows, you’re in full control — and by disabling Cloudflare’s automatic builds, you avoid unnecessary redeployments.

This setup is lightweight, scalable, and gives you the flexibility to integrate more advanced CI/CD practices in the future.

Happy building! 🚀