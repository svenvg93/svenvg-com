---
title: Selfhost a Single Sign-on MFA with Authentik
description: Selfhost a iDP for your homelab.
date: 2024-07-22
draft: false
categories:
  - Security
  - Zero Trust
tags:
  - authentik
  - docker
  - sso
cover: cover.jpg
---

Managing authentication and access control for self-hosted applications can be complex. Authentik, an open-source identity provider, simplifies this with features like single sign-on (SSO), multi-factor authentication (MFA), and seamless integration with various apps, enhancing security and user management.

In this post, we’ll walk you through setting up Authentik to streamline access control and strengthen security for your self-hosted services.

## Setting Up Authentik

First, create a directory to store the `docker-compose.yml` file

```bash
mkdir authentik
cd authentik
```

Next, create the `docker-compose.yml` file to set up the Docker container.

```bash
nano docker-compose.yml
```
Add the following configuration to the file:
```yaml {filename="docker-compose.yml"}
services:
  authentik-db:
    image: docker.io/library/postgres:16-alpine
    container_name: authentik-db
    restart: unless-stopped
    volumes:
      - authentik-db:/var/lib/postgresql/data
    environment:
      TZ: Europe/Amsterdam
      POSTGRES_PASSWORD: ${PG_PASS:?database password required}
      POSTGRES_USER: ${PG_USER:-authentik}
      POSTGRES_DB: ${PG_DB:-authentik}
    networks:
      - authentik
    env_file:
      - .env
  
  authentik-redis:
    image: docker.io/library/redis:alpine
    container_name: authentik-redis
    environment:
      TZ: Europe/Amsterdam
    command: --save 60 1 --loglevel warning
    restart: unless-stopped
    volumes:
      - authentik-redis:/data
    networks:
      - authentik
  authentik-server:
    image: ghcr.io/goauthentik/server:2024.6.0
    container_name: authentik-server
    restart: unless-stopped
    command: server
    environment:
      TZ: Europe/Amsterdam
      AUTHENTIK_REDIS__HOST: authentik-redis
      AUTHENTIK_POSTGRESQL__HOST: authentik-db
      AUTHENTIK_POSTGRESQL__USER: ${PG_USER:-authentik}
      AUTHENTIK_POSTGRESQL__NAME: ${PG_DB:-authentik}
      AUTHENTIK_POSTGRESQL__PASSWORD: ${PG_PASS}
    volumes:
      - authentik:/media
      - authentik:/templates
    networks:
      - authentik
    env_file:
      - .env
    ports:
      - 9000:9000
      - 9443:9443
    depends_on:
      - authentik-db
      - authentik-redis
  authentik-worker:
    image: ghcr.io/goauthentik/server:2024.6.0
    container_name: authentik-worker
    restart: unless-stopped
    command: worker
    environment:
      TZ: Europe/Amsterdam
      AUTHENTIK_REDIS__HOST: authentik-redis
      AUTHENTIK_POSTGRESQL__HOST: authentik-db
      AUTHENTIK_POSTGRESQL__USER: ${PG_USER:-authentik}
      AUTHENTIK_POSTGRESQL__NAME: ${PG_DB:-authentik}
      AUTHENTIK_POSTGRESQL__PASSWORD: ${PG_PASS}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - authentik:/media
      - authentik:/certs
      - authentik:/templates
    networks:
      - authentik
    env_file:
      - .env
    depends_on:
      - authentik-db
      - authentik-redis
volumes:
  authentik-db:
    name: authentik-db
  authentik-redis:
    name: authentik-redis
  authentik:
    name: authentik
networks:
  authentik:
    name: authentik

```

This setup will create both a database and a Redis instance alongside the Authentik Server and Worker. To enhance security, you’ll want to generate a database password and an Authentik secret key, then store these in an environment file.

Run the following command to generate a secure password for the database and a secret key for Authentik:

```bash
echo "PG_PASS=$(openssl rand 36 | base64 -w 0)" >> .env
echo "AUTHENTIK_SECRET_KEY=$(openssl rand 60 | base64 -w 0)" >> .env
```

Finally, start or restart the Authentik service to apply the changes:

```bash
docker compose up -d
```

Once all the containers have been successfully pulled and are running, navigate to the following URL in your web browser:

`http://<your server’s IP or hostname>:9000/if/flow/initial-setup/`

This will take you to the setup page for the admin user `akadmin.` Here, you’ll need to fill out the required fields to create your admin account. Ensure you provide the following information:

- Username: akadmin (or your preferred username)
- Password: Choose a strong password for the admin account
- Email: Enter a valid email address for account recovery or notifications

After filling in all the necessary fields, follow any additional prompts to complete the setup process. Once finished, you’ll be able to log in to the Authentik dashboard and start managing authentication and access control for your applications.

## Add Provider

To add a new provider in Authentik, follow these steps:

1. In the right-side menu, navigate to:
•	**Applications** -> **Provider**
2. Click on **Create** to start adding a new provider.
3. For the Provider Type, select **OpenID Connect**.
4. Enter a suitable Name for your provider to easily identify it later.
5. For the Authorization Flow, choose **explicit-content**.
6. Finally, click Finish to complete the setup of your OpenID Connect provider.

## Add Application

To create a new application in Authentik, follow these steps:

1. In the right-side menu, navigate to:
•	**Applications** -> **Applications**
2. Click on **Create** to initiate the application setup.
3. Enter your desired Name and Slug for the application.
4. If you have already created a provider, you can select it under Provider.
5. Click Next to proceed.
6. For the Provider, select **OpenID Connect**.
7. Click Next to continue.
8. For the Authorization Flow, c**explicit-content**.
9. Click Create to finalize the application setup.

### Retrieve Client ID and Secret

To use Authentik with your application, you will need the Client ID, Client Secret, and the required URLs:

1. In the Authentik dashboard, click on Edit for the provider you just created.
2. Here, you will find the **Client ID**, **Client Secret, URLs.**.
3. Fill in these details in the configuration settings of your connected application (such as Auth0) to complete the integration.
