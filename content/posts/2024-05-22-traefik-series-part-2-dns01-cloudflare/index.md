---
title: Traefik Series Part 2 | Using Let’s Encrypt DNS-01 Challenge with Cloudflare
description: In Part 2 of the Traefik series, learn how to obtain SSL certificates for your services using the Cloudflare DNS-01 challenge with Let’s Encrypt.
date: 2024-05-22
draft: false
categories:
  - Networking
  - Reverse Proxy
tags:
  - lets encrypt
  - cloudflare
  - traefik
cover: cover.jpg
---

Find a updated version of this guide in the [The Ultimate Guide to Setting Up Traefik](../the-ultimate-guide-to-setting-up-traefik/)

By default, Traefik uses the HTTP Challenge to obtain SSL certificates from Let’s Encrypt, verifying domain ownership via HTTP requests. However, the DNS-01 Challenge offers a more versatile alternative. It validates domain ownership through DNS records, making it ideal for securing subdomains or applications behind firewalls or NAT.

In this guide, we’ll configure the DNS-01 Challenge with Cloudflare to obtain SSL certificates from Let’s Encrypt. This method enables Traefik to manage certificates securely and efficiently, even in complex network setups, providing flexibility for homelabs and self-hosted environments.

If you need to setup Traefik from the beginning check [here](../traefik-series-part-1-reverse-proxy)

## Cloudflare API

To use the DNS-01 Challenge with Cloudflare, follow these steps to create the necessary API token:

1. Go to the Cloudflare [API page](https://dash.cloudflare.com/profile/api-tokens) and log in with your Cloudflare account.
2.	Create API Key:
  - Select **Create Token**.
  - Choose the template **Edit zone DNS**.
  - Ensure that the permissions are set to **Zone / DNS / Edit**.
  - Under **Zone Resources**, specify the domain for which the API key will be used.
  - Click **Continue** to summary.
3.	Review Token:
  - Review the token summary and make any necessary adjustments by selecting **Edit token**. Note that you can also edit the token after creation if needed.
4.	**Create Token** to generate the token’s secret.
5.	Save Your API Key: Make sure to save this API key securely, as you will need it later for configuring Traefik.

## Docker

To enable Traefik to use the DNS-01 Challenge with Cloudflare, you need to set up environment variables in your docker-compose.yml` file and securely store your Cloudflare credentials in a .env file. Follow these steps:

Add the following environment variables under the Traefik service in your <kbd>docker-compose.yml</kbd>:

```yaml
  environment:
    - CF_API_EMAIL=${CF_API_EMAIL}
    - CF_DNS_API_TOKEN=${CF_DNS_API_TOKEN}
```

In the same directory as your <kbd>docker-compose.yml</kbd>, create a <kbd>.env</kbd> file to securely store your Cloudflare credentials:

```bash
nano .env
```

Add the following content to the <kbd>.env</kbd> file, replacing the placeholders with your actual Cloudflare email and API token:

```bash
CF_API_EMAIL=<Your cloudflare email>
CF_DNS_API_TOKEN=<Your API Token>
```

This setup allows Traefik to access your Cloudflare account securely using the provided API credentials.

## Traefik Configuration

In your <kbd>traefik.yml</kbd> configuration file, you need to remove the <kbd>httpChallenge</kbd> part and add the <kbd>dnsChallenge</kbd> configuration. Here’s the complete updated <kbd>traefik.yml</kbd>:

```yaml
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
    network: proxy # Optional; Only use the "proxy" Docker network, even if containers are on multiple networks.
certificatesResolvers:
  letencrypt:
    acme:
      email: youremail@email.com
      storage: /certs/acme.json
      caServer: https://acme-v02.api.letsencrypt.org/directory # production (default)
      #caServer: https://acme-staging-v02.api.letsencrypt.org/directory # staging
      dnsChallenge:
        provider: cloudflare
        delayBeforeCheck: 10
```

After updating the configuration, you need to recreate the Traefik container for the environment variables to take effect. Run the following command:

```bash
docker compose up -d --force-recreate
```

With this setup, when Traefik needs to obtain a certificate, it will create a TXT record in your DNS zone using the Cloudflare API. Once the validation is completed, Traefik will automatically remove the TXT record, ensuring a seamless and efficient process for managing SSL certificates.
