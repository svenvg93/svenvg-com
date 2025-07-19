---
title: Setting Up Your Travel Router | Secure and Reliable Internet Anywhere
description: Learn how to set up your travel router for secure and reliable internet on the go. Stay connected anywhere!
date: 2025-04-05
draft: false
categories:
  - Networking
  - Router
tags:
  - travel router
cover: cover.jpg
---

Whether you're a digital nomad, a frequent traveler, or just someone who values a secure and stable internet connection on the go, a travel router can be a game-changer. In this guide, we'll walk you through everything you need to know about setting up your travel router—from choosing the right model securing your connection, and optimizing performance. Stay connected, stay secure, and make the most of your travel router wherever you go!

## Why

Building a travel router can be a game-changer, whether you're on the road for work, vacation, or digital nomad life. Here are four solid reasons to make one:

1. Better Security on Public Wi-Fi
Public networks in hotels, airports, and cafés are often insecure. A travel router lets you connect all your devices through a single, encrypted VPN tunnel, reducing exposure to potential threats.

2. Bypass Device Limits & Captive Portals
Some hotel Wi-Fi networks limit the number of connected devices or require logging in via a captive portal. A travel router can authenticate once and share the connection with all your devices, avoiding multiple logins.

3. Consistent Network for Your Devices
Keep your home-like network setup wherever you go. Your devices (laptop, phone, smart TV, etc.) will always connect to the travel router’s SSID, eliminating the need to reconfigure connections each time you switch locations.

4. Built-in VPN for Privacy
You can set up a VPN (WireGuard, OpenVPN) on your travel router to encrypt traffic.

## Hardware 

When it comes to a travel router, you want it to light and small. You don't want to carry your big heavy router from home with you. 

In terms of the hardware GL-Inet makes small Wifi routers in the size of a pack of cards. 
One of the best band for your buck devices is the Beryl AX. The GL.iNet Beryl AX (GL-MT3000) is a compact Wi-Fi 6 travel router equipped with the following specifications:​

- Processor: MediaTek MT7981B dual-core CPU running at 1.3 GHz.​
- Memory: 512MB DDR4 RAM.​
- Storage: 256MB NAND flash.​
- Wi-Fi Standards: Supports IEEE 802.11a/b/g/n/ac/ax protocols.​
- Wi-Fi Speeds: Delivers up to 574 Mbps on the 2.4 GHz band and up to 2402 Mbps on the 5 GHz band.​
- Antennas: Features two retractable external Wi-Fi antennas.​
- Ethernet Ports: One 2.5 Gbps WAN port, One 1 Gbps LAN port.​
- USB Ports: Includes one USB 3.0 Type-A port and one USB Type-C port for power input.​
- Power Supply: Requires a 5V/3A input via the USB Type-C port

Other reason to pick GL.iNet Beryl AX is that it runs OpenWRT, this applies to all GL.iNet devices. Their routers ship with a user-friendly UI, but you still have full access to the standard OpenWrt LuCI interface if you want deeper customization. This makes them great for both beginners and advanced users who need flexibility for things like VPNs, VLANs, ad-blocking, and more. 

## Initial setup

This setup is done with version <kbd>4.7.0</kbd> installed

During the initial setup you can either connect via a ethernet cable or to the default Wireless network of the Beryl. 

In order to login to the Beryl you have to go  <kbd>https://192.168.8.1</kbd>. This will prompt you a setup wizard to configure a login password to login to the UI.
As well as a the name and password for the wireless network. For now I leave the Wireless settings default, as I will change more settings later on. 

## Connect to Internet 

### Ethernet 

For the best possible experience, it's best to connect the Beryl with an Ethernet cable when you have the possibility. Some hotels and Airbnbs have an Ethernet cable connected to the TV for streaming services. If you don't need those, for example, when you bring your own streaming device, you can connect this cable to the WAN port of the Beryl. The Beryl will automatically pick up an IP address from the DHCP server.  

Please note that there might be security measures in place against this. If the Beryl does not get an IP address, the best option might be to connect the Beryl via WiFi as explained below.

### Connect to WiFi 

On the main dashboard, locate the **Repeater** section and click **Connect** to join the Beryl to an existing wireless network. Select the desired network, enter the password if required, and keep all other settings as default.  

If an authentication portal is needed, open a browser on your device to complete the login process.

### Wireless network

By default, the Beryl has separate networks for 2.4GHz and 5GHz. To simplify things, we'll give them the same name, allowing devices to automatically choose the best band based on signal strength and coverage.  

**Steps to configure**:  
1. **Go to** the **Wireless** section in the side menu.  
2. **Click on** <kbd>Modify</kbd>.  
3. **Set the TX Power to Medium**  
   - You can adjust this based on your preference. Since you'll likely be in a small space, there's no need for a strong Wi-Fi signal.  
4. **Change the SSID and Password** to your liking.  
5. **Set Wi-Fi Security** to **<kbd>WPA2-PSK/WPA3-SAE</kbd>** for optimal security.  
6. **Click Apply.**  

Repeat these steps for the 2.4GHz network.

Once you've updated the 2.4GHz network settings, your Beryl is ready to go—use it anywhere you like! 

In an later posts we will dive deeper in other options of the Beryl like DoH, Adguard Home etc.

Happy networking! 🤝
