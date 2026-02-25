---
title: Deploying a Hugo Site with Cloudflare Workers
description: Deploy your Hugo Website to Cloudflare Workers
date: 2025-07-20
draft: false
categories:
  - DevOps
  - CI/CD
tags:
  - hugo
  - cloudflare workers
cover: cover.jpg
series:
  - Static Site Deployment
---

I recently migrated my blog from Jekyll to Hugo — more on that soon. As part of the migration, I needed to set up deployments to Cloudflare. I typically use Cloudflare Pages, but when I went to configure it, I was met with a notice recommending Cloudflare Workers for new projects.

While Cloudflare hasn’t explicitly stated the future of Pages, it’s clear that the focus and innovation are shifting toward Workers.

In this post, I’ll walk you through how to set up your Hugo site for deployment using Cloudflare Workers.

## Add Worker Files to Your Repository

To enable deployment, you’ll need to add a `wrangler.jsonc` file. This configuration file tells Cloudflare how to build and serve your site correctly.

```jsonc {filename="wrangler.jsonc"}
{
  "name": "example-com",
  "compatibility_date": "2025-07-20",
  "assets": {
    "directory": "./public",
    "html_handling": "auto-trailing-slash",
    "not_found_handling": "404-page",
    "run_worker_first": false
  },
  "build": {
    "command": "hugo build --gc --minify",
  },
  "workers_dev": true,
  "preview_urls": true
}
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

Cloudflare will setup your domain and configure the DNS. It might take a few minutes before the domain name works. 

By combining Hugo and Cloudflare Workers, you now have a fast, reliable, and customizable static site deployment pipeline. 

This setup is lightweight, scalable, and gives you the flexibility to integrate more advanced CI/CD practices in the future.

Happy building!