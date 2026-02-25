---
title: Traefik Essentials Reverse Proxy with Docker & Let’s Encrypt
description: Master the art of deploying Traefik in your environment. This comprehensive guide covers everything from installation to advanced configuration for seamless traffic management in your homelab.
date: 2024-05-21
draft: false
categories:
  - Networking
  - Reverse Proxy
tags:
  - traefik
  - cloudflare
  - lets encrypt
cover: cover.jpg
series:
  - Traefik Essentials
---

## What is Traefik

Traefik is an open-source reverse proxy and load balancer, perfect for managing containerized applications in your homelab or home server. It integrates seamlessly with Docker, automatically detecting services, configuring routing, and securing connections with SSL. Designed for dynamic, self-hosted environments, Traefik adapts to changes in real-time, making it ideal for scaling and simplifying your setup.

In this guide, we will set up the Traefik Docker container, configure Let’s Encrypt for obtaining SSL certificates.

Let's get started!

## Setup Traefik with Docker

### Docker

Create the directory and `docker-compose.yml`

```bash
mkdir traefik
nano traefik/docker-compose.yml
```

Add the following configuration to the file:

```yaml {filename="docker-compose.yml"}
services:
  traefik:
    image: traefik
    container_name: traefik
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    environment:
      - TZ=Europe/Amsterdam
      - CF_API_EMAIL=${CF_API_EMAIL}
      - CF_DNS_API_TOKEN=${CF_DNS_API_TOKEN}
    networks:
      - frontend
    ports:
      - 80:80 # HTTP entryPoints
      - 443:443 # HTTPS entryPoints
      - 8080:8080 # Dashbaord WebGui 
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/traefik.yml:ro
      - traefik:/certs

volumes:
  traefik:
    name: traefik

networks:
  frontend:
    name: frontend
```

### Traefik configuration

Create a `traefik.yml` file to define Traefik's configuration settings. This file specifies key elements like entry points and providers, enabling Traefik to manage traffic routing, load balancing, and security effectively.

```bash
nano traefik/traefik.yml
```
Add the following configuration to the file:
```yaml {filename="traefik.yml" lineNos=true hl_lines=[29,31,36]}
api:
  dashboard: true
  insecure: true
  debug: false
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"
serversTransport:
  insecureSkipVerify: true
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
certificatesResolvers:
  letencrypt:
    acme:
      email: [youremail@email.com]
      storage: /certs/acme.json
      # caServer: https://acme-v02.api.letsencrypt.org/directory # prod (default)
      caServer: https://acme-staging-v02.api.letsencrypt.org/directory # staging
      # Use **one** of the following challenge types:
      # --- DNS Challenge (example: Cloudflare) ---
      dnsChallenge:
        provider: cloudflare
        delayBeforeCheck: 10

      # --- HTTP Challenge ---
      httpChallenge:
        entryPoint: web
```

Change `[youremail@email.com]` to your mail address

## Cloudflare API

This part is only needed when you choose for the DNS challenge

In this guide we use Cloudflare as DNS provider. You can follow the same steps for other DNS providers. Support list can be found [here](https://doc.traefik.io/traefik/https/acme/#providers).

To use the DNS-01 Challenge with Cloudflare, you need to create an API token that Traefik will use to authenticate with Cloudflare for automatic SSL certificate management.

1. Go to the Cloudflare [API page](https://dash.cloudflare.com/profile/api-tokens) and log in with your Cloudflare account.
2.	Create API Key:
  - Select **Create Token**.
  - Choose the template **Edit zone DNS**.
  - Ensure that the permissions are set to **Zone / DNS / Edit**.
  - Under **Zone Resources**, specify the domain for which the API key will be used.
  - Click **Continue** to summary.
3.	Review the token summary and make any necessary adjustments by selecting **Edit token**. Note that you can also edit the token after creation if needed.
4.	Click on **Create Token** to generate the token’s secret.
5.	Make sure to save this API key securely, as you will need it later for configuring Traefik.

In the same directory as your `docker-compose.yml`, create a `.env` file to securely store your Cloudflare credentials:

```bash
nano .env
```

Add the following content to the `.env` file, replacing the placeholders with your actual Cloudflare email and API token:

```bash {filename=".env"}
CF_API_EMAIL=<Your cloudflare email>
CF_DNS_API_TOKEN=<Your API Token>
```

## Start Traefik

Run the command below to start the container.

```bash
docker compose -f traefik/docker-compose.yml up -d
```

Then you can access the dashboard at http://serverip:8080.

## Add service

To verify Traefik is working correctly, we’ll set up a simple service using Traefik’s whoami application. This service provides basic HTTP responses displaying browser and OS information, which makes it ideal for testing.

Make a new directory called whoami to organize the service files.

```bash
mkdir whoami
nano whoami/docker-compose.yml
```

Add the following configuration to the file:

```yaml  {filename="docker-compose.yml"}
services:
  whoami:
    container_name: simple-service
    image: traefik/whoami
    labels:
        - "traefik.enable=true"
        - "traefik.http.routers.whoami.rule=Host(`test.example.com`)"
        - "traefik.http.routers.whoami.entrypoints=websecure"
        - "traefik.http.routers.whoami.tls=true"
        - "traefik.http.routers.whoami.tls.certresolver=letencrypt"
        - "traefik.http.services.whoami.loadbalancer.server.port=80"
```

### Setting Up DNS and Starting the Service

Update your domain’s DNS settings to point test.example.com (replace this with your actual domain) to your server’s IP address. Verify that the changes have propagated and the domain resolves to your IP using tools like nslookup or online DNS checkers.

Open your browser and navigate to your domain to check if a certificate from the Let's Encrypt Staging server is being used. You should see a certificate warning, as staging certificates are not trusted by browsers. This confirms that the staging configuration is working as expected.

## Production Certificates
Now that everything is functioning correctly, it's time to switch the caServer to the production version to obtain trusted certificates. Additionally, we need to remove the staging certificates; otherwise, Traefik will not request new ones. 
Stop the running Traefik container and remove the volume used.

```bash
docker compose -f traefik/docker-compose.yml down
docker volume rm traefik
```

Open your `traefik.yml` file and modify the `caServer` setting to point to the production Let's Encrypt server. Comment out the staging line and ensure the production line is active, as shown below:

```yaml {filename="traefik.yml"}
caServer: https://acme-v02.api.letsencrypt.org/directory # prod (default)
# caServer: https://acme-staging-v02.api.letsencrypt.org/directory # staging
```

After updating the configuration and clearing the staging certificates, restart Traefik to request production certificates.

```bash
docker compose -f traefik/docker-compose.yml up -d
```

You can use the same test service we made before the check if you now get the trusted certificates.

Some browsers keep a hold on the previous served certificates for some time. If you still get the staging certificate, try another browser or incognito window

Great! Now that everything is confirmed to be working in production, you can clean up by removing the test whoami service. Simply stop and remove the whoami container, and delete its configuration from your Docker Compose file. This cleanup will leave your setup streamlined, retaining only the essential configuration and services for your production environment.
