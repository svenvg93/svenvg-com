---
title: Deploying a Hugo Site with Github Actions to Cloudflare Workers
description: Deploy your Hugo Website to Cloudflare with Github Actouns
date: 2025-07-20
draft: true
categories:
  - DevOps
  - CI/CD
tags:
  - hugo
  - github actions
  - cloudflare workers
cover: cover.jpg
---

Cloudflare can automatically rebuild your site when changes are pushed to your repository. However, for greater control over the deployment process, you can trigger builds using GitHub Actions.

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

### Get Your Cloudflare Account ID

1. In the Cloudflare dashboard, go to your Account Home
2. Click the three-dot menu next to your account name
3. Click Copy Account ID
4. Save this ID securely — it will also be added to GitHub Secrets

### Add GitHub Secrets

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

These values are encrypted and accessible only during workflow execution.

### Workflow

With all the access methods configured, the next step is to create the workflow file.
Create a file named `deploy.yml` inside the `.github/workflows` directory of your repository.

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
With everything in place—custom build settings, GitHub Actions integration, and Cloudflare Worker deployment—you now have full control over how and when your Hugo site is built and published. This setup not only ensures reproducibility but also keeps your build process fast, clean, and flexible.

By using GitHub Actions, you can easily extend or schedule deployments, while disabling Cloudflare’s automatic builds avoids duplicate work.

That’s it! Your Hugo site is now running on Cloudflare Workers with a modern CI/CD pipeline.