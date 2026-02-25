---
title: Selfhost your website analytics with Umami
description: Learn how to self-host your website analytics using Umami, a privacy-focused and open-source analytics platform.
date: 2025-01-29
draft: false
categories:
  - Analytics
tags:
  - umami
  - web analytics
  - docker
  - privacy
cover: cover.jpg
---
Umami is an open-source, privacy-focused web analytics tool that serves as an alternative to Google Analytics. It offers essential insights into website traffic, user behavior, and performance while prioritizing data privacy. Unlike many traditional analytics platforms, Umami does not collect or store personal data, ensuring compliance with GDPR and PECR, and eliminating the need for cookies.

What makes Umami even more appealing is that it can be self-hosted, giving you full control over your data. In this guide, we’ll walk through the process of setting up Umami on your own server and exposing it via Cloudflare Tunnel, allowing it to securely collect the analytics sent by your website, all while maintaining privacy.


## Setup Umami

To set up Umami, we need to create a folder to hold both the `docker-compose.yml` and the configuration file.

First, create the folder for Umami:
```bash
mkdir umami
```

Open a new `docker-compose.yml` file for editing:

```bash
nano umami/docker-compose.yml
```
Paste the following content into the file:
```yaml {filename="docker-compose.yml"}
services:
  umami:
    image: ghcr.io/umami-software/umami:postgresql-latest
    container_name: umami
    ports:
      - "8083:3000"
    environment:
      DATABASE_URL: postgresql://umami:umami@umami-postgresql:5432/umami
      DATABASE_TYPE: postgresql
      APP_SECRET: ${UMAMI_SECRET}
    restart: unless-stopped
    env_file: .env
    depends_on:
      umami-postgresql:
        condition: service_healthy
  umami-postgresql:
    image: postgres:15-alpine
    container_name: umami-postgresql
    environment:
      POSTGRES_DB: umami
      POSTGRES_USER: umami
      POSTGRES_PASSWORD: umami
    volumes:
      - umami-postgresql-db:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-bash", "pg_isready -U umami -d umami"]
      interval: 60s
      timeout: 5s

volumes:
  umami-postgresql-db:
```

### Generate and Store the App Secret

Before starting Umami, you’ll need to generate an application secret. This secret is used to securely start the application. Here’s how to generate it:

```bash
openssl rand 30 | openssl base64 -A
# Example output : grYw1gf2CurwJqgyuVCJD9A9xa7pDKzvA1kmzDry
```

Once you’ve generated the secret, add it to your `.env` file for use by your Umami container:

```bash
nano umami/.env
```

Paste the following content into the file:

```bash {filename=".env"} 
UMAMI_SECRET=grYw1gf2CurwJqgyuVCJD9A9xa7pDKzvA1kmzDry
```
### Start Umami Analytics

Finally, start the Umami services by running the following commands:

```bash
docker compose -f umami/docker-compose.yml up -d
```

## Configure Cloudflare Tunnel

Setting up the Cloudflare tunnel is out of scope for this post. Check out this [post](../cloudflare-tunnel-secure) if you want to know how to set it up.

Now we need to add Umami to the Cloudflare Tunnel on the Zero Trust page to ensure it can be accessed securely.

1. Go to the Networks -> Tunnels page in your Cloudflare dashboard.
2. Click on the Tunnel you want to add Umami to.
3. Click on Edit.
4. Navigate to Public Hostname and click on Add a public hostname.
5. Fill in the following fields:
- **Subdomain** : Enter your desired subdomain.
- **Domain** Select your domain from the list.
- **Type** : Choose HTTP.
- **URL** : If Umami and Cloudflare Tunnel are on the same Docker network, you can use its container name and port number in the URL, like this: umami:3000.
6. After saving, you can now access Umami via the tunnel. Log in to the management interface using the domain name you just created.

Make sure that the Domain you choose for your Umami instance is not easily associated with analytics, as ad blockers may block domains with “analytics” in their names.

## Add a website

Now we need to add the website we want to analyze to Umami.

1. Log into Umami (default login is `admin/umami`) and click on **Settings** in the header.
2. Navigate to **Websites** and click the **Add Website** button.
3. Fill out the form with the following details and click **Save**:
   - The **Name** field can be anything you prefer, but it's typically the same as your domain name.
   - The **Domain** field should be the actual domain of your website. This helps filter out your own website from the referrer list in your analytics.
4. Once the website is added, you’ll need the **Website ID** to link it to the site you want to track.
5. Click on **Edit** next to the website you just created.
6. Copy the **Website ID** for use in your tracking setup.

Don't forget to change the username and password, as this website will be accessible for everyone

## Add the Website ID to Your Website

Now you can add the Website ID to your website, according to their instructions. In this example we add it to a [Jekyll blog with the Chripy theme](../jekyll-chirpy-cloudflare-pages).

Fill in your own data into `_config.yml` to integrate Umami analytics.
(search for umami in config file)

```yaml
umami:
  id: "19e0f843-ddd1-4841-b112-e21f6a750770" # fill in your Umami ID
  domain: "https://umami.yourdomain.com"     # fill in your Umami domain
```
Ensure `JEKYLL_ENV=production` environment variable is set when running jekyll build to apply production specific features such as web analytics.
