---
title: How I use GitHub Actions to update my blog daily
description: A step-by-step guide on automating the deployment of your blog using GitHub Actions for continuous publishing.
date: 2025-01-31
draft: false
categories:
  - DevOps
  - CI/CD
tags:
  - github actions
  - jekyll
  - cloudflare pages
cover: cover.jpg
---

This blog is hosted on Cloudflare Pages for optimal loading speed. As a static website built with Jekyll and the Chirpy theme, it relies on a trigger to prompt Cloudflare to rebuild and publish the site. In a previous post, I showed how to set up [Jekyll with Cloudflare Pages](../jekyll-chirpy-blog-on-cloudflare-pages/), where Cloudflare monitors your Git repository and automatically rebuilds the site with every merge or commit.

Jekyll allows posts to be scheduled based on the date in the frontmatter, so I often write posts in advance while working on something new. This means there won’t always be a commit or merge to trigger a rebuild on the right date to publisch a post. Instead of only relying on Cloudflare to watch the repository, we needed a trigger to rebuild the site. This is where GitHub Actions comes in.

In this post, we’ll configure GitHub Actions to integrate with Cloudflare Webhooks, enabling automatic rebuilds of your blog—whether triggered on-demand or according to a set schedule.

## Cloudflare Webhooks 

Cloudflare provides the ability to create webhooks for Pages projects. A webhook is essentially a unique URL that listens for incoming HTTP POST requests. When this URL receives a POST request, it triggers a specific action — in this case, starting a new build for your Pages project.

Steps to Set Up a Webhook
1. Log in to the [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Navigate to **Compute (Workers)** → **Workers & Pages**.
3. Open the project for which you want to set up the webhook.
4. Go to the **Settings** tab and click the **+** icon next to **Deploy Hooks**.
5. Provide a name for your webhook.
6. Click **Save**.
7. Copy the text under **Test by sending a POST request**. Save this information, as it will be needed in the next step.

### Github Secrets
We need to configure GitHub to use the Webhook for deployment. Since this information is sensitive, we don’t want it to be visible to anyone. To secure it, we use GitHub Secrets to store this data in the repository. These secrets are encrypted and can only be accessed by the GitHub Action during workflow execution.

1. Go to your project's repository in GitHub.
2. Under your repository's name, select **Settings**.
3. Select **Secrets** > **Actions** > **New repository secret**.
4. Create the following secrets:
- CLOUDFLARE_WEBHOOK
  - In the Name field, enter **CLOUDFLARE_WEBHOOK**.
  - In the Value field, enter your wehbook you must make sure it's between "": `"https://api.cloudflare.com/client/v4/pages/webhooks/deploy_hooks/blablalbalbala"`


## Github Action

Create a `.github/workflows/pages-deployment.yaml` file at the root of your project. The `.github/workflows/pages-deployment.yaml` file will contain the jobs you specify on the request.

```yaml {filename="pages-deployment.yaml"}
name: Daily build Cloudflare Pages
on:
  workflow_dispatch:
  schedule:
    - cron: "0 9 * * *"

jobs:
  webhook:
    name: Sent Webhook Trigger
    runs-on: ubuntu-latest
    steps:
      - name: Use curl to send webhook
        run: |
          curl -X POST {% raw %}${{ secrets.CLOUDFLARE_WEBHOOK }}{% endraw %}
```

Now, every day at 09:00 UTC, Cloudflare is triggered to rebuild and republish the website.
