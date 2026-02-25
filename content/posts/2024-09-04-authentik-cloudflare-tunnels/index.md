---
title: Secure your Cloudflare Tunnel with Authentik
description: Configure Authentik as Zero Trust IdP for Cloudflare Tunnel.
date: 2024-09-04
draft: false
categories:
  - Security
  - Zero Trust
tags:
  - cloudflare tunnel
  - authentik
  - sso
cover: cover.jpg
series:
  - Authentik
---
Enhancing the security and accessibility of your self-hosted applications is simplified with the right tools. By leveraging Cloudflare Tunnels and Authentik, you can create a powerful combination that fortifies your setup. Cloudflare Tunnels allow you to securely expose your local server to the internet, concealing your IP address and eliminating the need for port forwarding. In tandem, Authentik provides robust authentication and access control features.

This blog post will guide you through the process of integrating Cloudflare Tunnels with Authentik, demonstrating how to secure your self-hosted services effortlessly.

## Create an Application in Authentik for Cloudflare

First, we need to set up an application in Authentik for Cloudflare. In the Authentik Web GUI, navigate to the right side menu and click on Applications -> Applications. Then, click on Create with Wizard.

1. Enter a Name and Slug for your application. For this example, we’ll use cf-tunnel-access.
2. Click Next.
3. For the Provider, select OpenID Connect.
4. Click Next, and for the Authorization flow, choose explicit-content.
5. Finally, click Submit to create the application.


## Cloudflare Tunnel

Now we need to add Authentik to the Cloudflare Tunnel on the Zero Trust page to ensure it can be accessed securely.

1. Go to the Networks -> Tunnels page in your Cloudflare dashboard.
2. Click on the Tunnel you want to add Authentik to.
3. Click on Edit.
4. Navigate to Public Hostname and click on Add a public hostname.
5. Fill in the following fields:
- **Subdomain** : Enter your desired subdomain.
- **Domain** Select your domain from the list.
- **Type** : Choose HTTP.
- **URL** : If Authentik and Cloudflare Tunnel are on the same Docker network, you can access Authentik using its container name and port number in the URL, like this: authentik-server:9000.
6. After saving, you can now access Authentik via the tunnel. Log in to the management interface using the domain name you just created.

Next, we need to gather some information for the provider we just created in Authentik:

1. On the right side menu, click on Applications -> Providers.
2. Click on the cf-tunnel-access provider. You will see some URLs that are needed for Cloudflare.
3. On the Cloudflare Zero Trust page, go to Settings -> Authentication -> Add New -> OpenID Connect.
4. Fill in the following fields with the provider information:
- **Name** : Enter a name for your OpenID Connect provider.
- **Auth URL** : Use the Auth URL from Authentik.
- **Token URL** : Use the Token URL from Authentik.
- **Certificate URL** : This is the JWKS URL in Authentik.
5. In Authentik, click Edit on the provider. You will find a Client ID and Client Secret. Enter these values in Cloudflare as App ID and Client Secret, respectively.
6. Click Save after filling in all the information.
7. To test the integration, click on Test on the overview page. It should redirect you to Authentik. Log in with your account, and if everything works correctly, you will see a success page.

## Assign Authentication Method to Applications

The final step is to assign this authentication method to the applications you want to secure through the tunnel:

1. On the Zero Trust page, go to **Access** -> **Applications**.
2. Edit the Application you want to change.
3. Navigate to **Authentication**. Uncheck Accept all available identity providers and ensure that OpenID Connect is selected.
4. Click **Save Application**.

Now, when you try to access the application, you will be prompted to log in using Authentik.
