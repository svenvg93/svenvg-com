---
title: Deploy Zensical on Cloudflare Workers
description: Build a documentation site with Zensical on Cloudflare Workers
date: 2026-01-01
draft: false
categories:
  - Documentation
  - CI/CD
tags:
  - cloudflare worker
  - zensical
cover: cover.jpg
series:
  - Static Site Deployment
---

After the announcement that Material for MkDocs is put on [maintenance mode](https://github.com/squidfunk/mkdocs-material/issues/8523). I had to search for an alternative to keep my documentation sites up to date and secure. Luckily the search was short. The team behind Material for MkDocs launched Zensical as a new modern replacement.

In this guide, we’ll walk through installing and configuring Zensical. We’ll set up the site, create pages using Markdown, and deploy it for free on Cloudflare Workers.

## GitHub

To kickstart your Zensical deployment you can use the template I created, by following the steps below.

1.	Go to my [zensical-starter-template](https://github.com/svenvg93/zensical-starter-template) repository.
2.	Click on **Use this template** at the top of the repository page.
3.	Select **Create a new repository** from the dropdown.
4.	Give your new repository a unique name and click Create repository to finish.

This will create a copy of the template in your GitHub account, ready for customization!

## Set Up Cloudflare Workers

Once you’ve prepared the repository, it’s time to deploy your site on Cloudflare Pages. Here’s how:

1.	Visit [Cloudflare Dashboard](https://dash.cloudflare.com/).
2.	Go to **Compute & AI** -> **Workers & Pages**.
3.	Click on **Create Application**.
4.	Select **Continue with Git** and, if prompted, link your GitHub account.
5.	Choose the new repository you created from the template and click **Next**.
6.	In the build settings keep everything default.
7.	Click Save and Deploy.

Cloudflare will now clone your GitHub repository, build your Zensical site, and publish it.

Once the deployment succeeds, click **Continue Project**. Cloudflare assigns a domain to your site, like zensical-em9.pages.dev.

- The free plan allows up to 500 builds per month.
- DNS propagation may take a few minutes, so be patient as your site becomes accessible.

### Custom Domain

To use your custom domain name with the website, follow these steps to link it.

*   Click **Custom Domain**
*   Go to **Set up a Custom Domain**
*   Enter the name, click **continue**
*   Check the information and click **Activate Domain**

It will create a **CNAME** DNS record for your domain pointing to the generated name earlier.

## Set up the Site

Great! Now that your site is live, let’s start by adding some content to make it look complete.

### Clone repository

First, clone the repository you created from the template:

```bash
git clone git@github.com:<YOUR-USER-NAME>/<YOUR-REPO-NAME>.git
cd YOUR-REPO-NAME
```

### Adjust information

Open the `zensical.toml` file to adjust the **site_name**.

```bash
nano zensical.toml
```

```yaml {filename="zensical.toml"}
site_name: My Docs
```

### Create Your First Page

Navigate to the docs folder and create a new markdown file:

```bash
cd docs
nano firstguide.md
```

In this file, add a title and some content:

```markdown {filename="firstguide.md"}
---
title: Lorem ipsum dolor sit amet 
---
# Welcome to the first page
Lorem ipsum dolor sit amet
```

Zensical offers a wide range of layout and customization options for your pages. You can explore the [Zensical Reference Guide](https://zensical.org/docs/setup/basics/) for additional styling and layout options.

### Publish post

Since your site’s content is managed in a GitHub repository, Cloudflare automatically monitors it for changes. Each commit or merge triggers a rebuild and republish of the website.

To publish a new post, just run these commands in your repository:

```bash
git add .
git commit -m "First Post"
git push
```

Cloudflare will detect the changes, rebuild your site, and publish the latest version. You can track the progress under Deployments in Cloudflare Workers & Pages.


Congrats! You’ve now set up and published documentation using Zensical and Cloudflare Workers.