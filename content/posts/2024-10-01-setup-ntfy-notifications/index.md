---
title: Setup ntfy for selfhosted notifications
description: Selfhosted notifications for your homelab with ntfy & Cloudflare.
date: 2024-10-01 09:00:00 +0200
draft: false
categories:
  - Self-Hosting
tags:
  - ntfy
  - notifications
  - docker
cover: cover.jpg
---
In today’s world, staying informed about events in our homelabs is essential. ntfy is a straightforward HTTP-based notification service that allows you to send notifications to your phone or desktop from any computer using scripts or a REST API. The best part? You can host it entirely within your own homelab.

In this guide, we’ll show you how to make ntfy publicly accessible through Cloudflare Tunnels, ensuring you receive notifications wherever you are.

Setting up Cloudflare tunnels is out of scope for this article see [here](https://medium.com/@svenvanginkel/self-hosting-securely-with-cloudflare-zero-trust-tunnels-0a9169378f78) if you want to set it up.

## Setup ntfy with Docker

To get started with ntfy, you’ll need to create the necessary directories and files for the Docker container.

```bash
mkdir ntfy
```
Create a docker-compose.yml file:
In the ntfy folder, create a docker-compose.yml file:

```bash
nano ntfy/docker-compose.yml
```
Add the following content to the file:
```yaml {filename="docker-compose.yml"}
services:
  ntfy:
    image: binwiederhier/ntfy:v2.11.0
    container_name: ntfy
    restart: unless-stopped
    environment:
      - TZ=Europe/Amsterdam  # Change this to your timezone
      - NTFY_BASE_URL=http://ntfy.yourdomain.com
      - NTFY_CACHE_FILE=/var/lib/ntfy/cache.db
      - NTFY_BEHIND_PROXY=true
      - NTFY_ATTACHMENT_CACHE_DIR=/var/lib/ntfy/attachments
      - NTFY_UPSTREAM_BASE_URL=https://ntfy.sh # Optional if you need push notifications on iOS
    volumes:
      - ntfy:/var/lib/ntfy
    command:
      - serve
    networks:
      - cloudflared
volumes:
  ntfy:
    name: ntfy
networks:
  cloudflared:
    name: cloudflared
```

The cloudflared network should correspond to the Docker network where your Cloudflare tunnel is active. Adjust this part according to your setup.

Run the following command to start the container:

``` bash
docker compose -f ntfy/docker-compose.yml up -d
```

## Cloudflare Tunnel

Here’s a refined version of the instructions for adding ntfy to the Cloudflare Tunnel:

Adding ntfy to Your Cloudflare Tunnel

To make ntfy accessible via the Cloudflare Tunnel, follow these steps:

1. Navigate to the Tunnels Page:
Go to the Networks -> Tunnels section in your Cloudflare dashboard.
2. Select Your Tunnel:
Click on the tunnel to which you want to add ntfy.
3. Edit Tunnel Settings:
Click on Edit to modify the tunnel settings.
4. Configure Public Hostname:
- Go to the Public Hostname section.
- Click on Add a public hostname.
5. Fill in the Required Fields:
- Subdomain: Choose a subdomain (e.g., ntfy).
- Domain: Select your domain from the dropdown list.
- Type: Select HTTP.
- URL: Use the container name for the URL, which would be ntfy.
6. Access Your ntfy WebGui:

After saving the configuration, you can access the ntfy WebGui at https://ntfy.yourdomain.com.


## Test Notifications

1. Open the ntfy WebGui:
Navigate to https://ntfy.yourdomain.com.
2. Subscribe to a Topic:
- Click on Subscribe to topic.
- You can either create a new topic with your preferred name or generate a random topic name for added security.
3. Send a Test Notification:
Open the command line on your server and run the following command:

Open the command line on your server and run the following command:

```bash
curl -d "Hi" https://ntfy.yourdomain.com/yourtopic
```

Replace yourtopic with the name of the topic you just created in the WebGui.

After sending the command, you should see the message “Hi” appear in the WebGui under the subscribed topic.

## Secure it

To enhance the security of your ntfy setup by requiring authentication, you can update your docker-compose.yml file as follows:

Open the docker-compose.yml file:
```bash
nano ntfy/docker-compose.yml
```
Add the following environment variables
```yaml {filename="docker-compose.yml"}
environment:
  - NTFY_AUTH_FILE=/var/lib/ntfy/auth.db
  - NTFY_AUTH_DEFAULT_ACCESS=deny-all
  - NTFY_ENABLE_LOGIN=false
```

Run the following command to restart the container and apply the changes:

``` bash
docker compose -f ntfy/docker-compose.yml up -d --force-recreate
```

## Users


To manage users and their permissions in your ntfy setup, follow these steps to create users and assign them specific access rights:

Login to the ntfy Docker container
```bash
docker exec -it ntfy sh
```

### Create admin user
To create an admin user who can read and write to all topics, use the following command:

```bash
ntfy user add --role=admin <username>
```

Congrats, you have now your know service for sending push notifications for all your applications.
