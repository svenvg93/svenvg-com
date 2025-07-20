---
title: Managing Portainer Stacks Using GitOps
description: "Automate Your Docker Stack Management and Deployments with Portainer and GitOps."
date: 2025-07-07
draft: false
categories:
  - DevOps
  - CI/CD
tags:
  - docker
cover: cover.jpg
---

Container orchestration can quickly become complex as your infrastructure grows. By combining Portainer’s intuitive UI with a GitOps workflow, you can declaratively manage your Docker stacks and enjoy both transparency and reproducibility. In this post, we’ll walk through the process of installing Portainer, configuring GitOps using a Git repository, and automating deployments of your Docker stacks.

## Why GitOps with Portainer?

- **Declarative Infrastructure**: Store your stack definitions (Compose files, environment variables, configs) in Git — your single source of truth.
- **Version Control & Auditability**: Every change is tracked, making rollbacks and audits straightforward.
- **Self-Service Deployments**: Propose changes via pull requests, fostering collaboration and code review.
- **Automated Sync**: Portainer’s GitOps integration will automatically reconcile your live environment with the desired state in Git.


## Install Portainer
The first step is to install Portainer on the host where you plan to manage your Docker Compose stacks. 

In this series, I’m using the Enterprise Edition of Portainer to unlock all the necessary features. You can request your free 3-node license here: https://www.portainer.io/take-3

You can use the following Docker Compose snippet to get started:

```yaml {filename="docker-compose.yml"}
services:
  portainer:
    image: portainer/portainer-ee:2.31.3
    container_name: portainer
    restart: unless-stopped
    environment:
      TZ: Europe/Amsterdam
      PUID: 1000
      PGID: 1000
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer:/data
    ports:
    - 8000:8000
    - 9443:9443
volumes:
  portainer:
    name: portainer
```
## Create Github Access Token
To grant Portainer access to your GitHub repository, you’ll need a Personal Access Token:

1. Navigate to **Settings** → **Developer settings** → **Personal access tokens** in your GitHub account or go directly to:
    https://github.com/settings/personal-access-tokens/
2. Click **Generate new toke**n and choose **Fine-grained token**.
3. Under **Repository access**, assign:
  - **Read access** to metadata
  - **Read & write access** to code

Complete the token creation, then copy and store the token securely — you’ll use it when configuring GitOps in Portainer.

## Deploy your stack

Once you’ve connected your Git repository to Portainer (with your PAT), you can provision and manage stacks directly from Git. Here’s how:

1. Open the **Portainer UI**
2. Log in to Portainer and select the environment (endpoint) where you want to deploy your stack.
3. Navigate to **Stacks**
4. In the sidebar, click Stacks. This shows your existing stacks and lets you add new ones.
5. Add a New Stack
6. Click the **+ Add stack** button.
7. Name: Give the stack a friendly name (e.g. nginx-gitops).
8. In the Build method options, choose **Git repository**.

### Configure the Git Repository

- **Enable Authentication** for your GitOps repository in Portainer.
- **Username**: Enter your GitHub username.
- **Personal Access Token**: Paste the fine-grained token you generated on GitHub.
- **Repository URL**: Provide the HTTPS clone URL of your repo (for example, https://github.com/yourorg/docker-stacks-gitops.git).
- **Compose Path**: Specify the relative location of your docker-compose.yml file in the repository. For example `nginx/docker-compose.yml`


### Git Updates
To enable Portainer to automatically sync and deploy changes from your Git repository, turn on GitOps updates.

- **GitOps updates**: Toggle this option to have Portainer periodically pull and apply commits from your repo. Configure the sync interval to match your workflow.

- **Local filesystem paths**: List any extra directories your stack relies on—e.g. `/nginx/config/`. These paths must also exist in your Git repository so Portainer can include them during each sync.

### Environment Variables & Secrets (optional)
If your `docker-compose.yml` references environment variables, expand the **Environment variables** section and add key/value pairs.

### Deploy
- Click **Deploy the stack**
- Portainer will clone the repo, read the Compose file, and spin up the services defined in it.


## Verify & Monitor
After deployment, Portainer displays each service’s status in the Stack details.
To view logs, click a service and select Logs. Any subsequent commits to that repo path will trigger an automatic redeploy if GitOps Updates is enabled — or you can manually click Update the stack.

With these steps, you’ve implemented a GitOps workflow: your Docker stacks live in Git, and Portainer continuously reconciles your live environment to match that source of truth. Happy deploying!
