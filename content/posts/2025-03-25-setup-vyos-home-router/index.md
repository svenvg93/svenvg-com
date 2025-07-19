---
title: Setting up VyOS router for your home network
description: Setting up a VyOS router for your homelab gives you enterprise-grade networking with open-source flexibility.
date: 2025-03-25
draft: false
categories:
  - Networking
  - Router
tags:
  - vyos
  - firewall
cover: cover.jpg
---

Setting up a [VyOS](https://vyos.io) router for your homelab gives you enterprise-grade networking with open-source flexibility. In this post, we'll cover the essential steps to install and configure VyOS for a more secure and efficient network.

VyOS provides a free routing platform that competes directly with other commercially available solutions from well-known network providers. Because VyOS is run on standard amd64 systems, it can be used as a router and firewall platform for cloud deployments.

VyOS offers powerful routing, firewalling, making it an excellent choice for homelabbers who want more than what consumer routers can provide. In this post, we’ll walk you through the essential steps to install and configure VyOS, so you can build a more secure and efficient network tailored to your needs.

## Installation

VyOS can run on various diffrent platforms. Both baremetal as well als cloud platforms. In this guide we will use the "bare metal" installation inside of a VM.

After you [download](https://github.com/vyos/vyos-nightly-build/releases) the latests version, boot from the image using the appropriate method for your platform (USB, virtual machine, or PXE).

VyOS rolling release images are built from the latest development code, incorporating the newest changes from maintainers and community contributors. While they receive automated testing to ensure they boot and load configurations, they may include experimental features, bugs, and compatibility issues. As a result, they are not recommended for production use.

Once the image loads, log in with the default credentials (<kbd>vyos/vyos</kbd>). In operational mode, run <kbd>install image</kbd> and follow the wizard. It will guide you through partitioning the disk and configuring the root password. After installation, remove the live USB or CD and reboot the system.

## Operational modes

VyOS has two main operational modes: Operational Mode and Configuration Mode. Understanding these modes is key to managing and configuring the system effectively.

- *Operational Mode*: This is the default mode when you log in. It’s used for monitoring, troubleshooting, and running system commands. Here, you can check interfaces, view logs, test connectivity, and restart services. Commands in this mode do not change the system’s configuration
- *Configuration Mode*: This mode is used to modify the system’s settings. To enter configuration mode

We need to enter configuration mode to configure our initial setup.

```shell
configure
```

## LAN

We’ll configure the LAN ports to establish a network connection for all your devices. This will ensure that both your homelab and internet access are set up properly, providing seamless connectivity throughout your network.

### Bridge Interface

We’ll create a bridge interface, allowing us to combine all the ports into a single network. This will enable seamless communication between all your devices on the same network.


```shell
set interfaces bridge br0 
set interfaces bridge br0 description LAN bridge
set interfaces bridge br0 address 192.168.1.1/24
set interfaces bridge br0 member interface eth0
commit; save
```

In this setup I only have one interface in the bridge. You repeat the <kbd>interfaces bridge br0 member interface eth0</kbd> command for every interface you want to be part of the bridge.

You can check the bridge with the command <kbd>run show bridge br0</kbd>


```shell
admin@BR01:~$ run show interfaces bridge 
Codes: S - State, L - Link, u - Up, D - Down, A - Admin Down
Interface        IP Address                        S/L  Description
---------        ----------                        ---  -----------
br0              192.168.1.1/24                    u/u 
```

When in Configuration Mode, you normally can't run operational commands like <kbd>show</kbd>. However, you can use <kbd>run</kbd> before the command to execute it without leaving Configuration Mode.

### DHCP

Now, we’ll set up a DHCP server to automatically assign IP addresses to all the devices connected to your network.

```shell
set service dhcp-server shared-network-name LAN authoritative
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 lease 86400
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 option default-router 192.168.1.1
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 option name-server 192.168.1.1
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 range 0 start 192.168.1.100
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 range 0 stop 192.168.1.200
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 subnet-id 1
commit; save
```

To view active leases from connected clients, use the command: <kbd>run show dhcp server leases</kbd>

```shell
admin@BR01:~$ run show dhcp server leases
IP Address     MAC address        State    Lease start                Lease expiration           Remaining    Pool    Hostname     Origin
-------------  -----------------  -------  -------------------------  -------------------------  -----------  ------  -----------  --------
192.168.1.100  bc:24:11:82:b2:20  active   2025-03-19 17:31:03+00:00  2025-03-20 17:31:03+00:00  23:41:55     LAN     ubuntu-test  local
192.168.1.101  bc:24:11:89:c8:77  active   2025-03-19 17:36:13+00:00  2025-03-20 17:36:13+00:00  23:47:05     LAN     ubuntu-test  local
```



## WAN

As a next step we will configure our WAN internet connection. As we need this interface for the next steps we will configure it first. 
In my case I use a VLAN (vif) interface with DHCP, as it is required by my ISP. 

Be sure to replace the placeholder variables [inside brackets] with values specific to your setup.

```shell {filename="DHCP with VLAN"}
set interfaces ethernet [YOUR_ETHERNET_INTERFACE] vif [VLAN_ID] address dhcp
set interfaces ethernet [YOUR_ETHERNET_INTERFACE] vif [VLAN_ID] description WAN-Interface
commit; save
```

```shell {filename="DHCP"}
set interfaces ethernet eth1 address dhcp
set interfaces ethernet eth1 description WAN-Interface
commit; save
```
 
```shell {filename="PPPoE with VLAN"}
set interfaces ethernet [YOUR_ETHERNET_INTERFACE] vif [VLAN_ID] description WAN-Interface
set interfaces pppoe pppoe0 authentication username [YOUR_USERNAME]
set interfaces pppoe pppoe0 authentication password [YOUR_PASSWORD]
set interfaces pppoe pppoe0 source-interface [YOUR_ETHERNET_INTERFACE].[VLAN_ID]
set interfaces pppoe pppoe0 default-route auto
set interfaces pppoe pppoe0 mtu 1492
set interfaces pppoe pppoe0 description WAN-Interface
commit;save
``` 

```shell {filename="PPPoE"}
set interfaces pppoe pppoe0 authentication username [YOUR_USERNAME]
set interfaces pppoe pppoe0 authentication password [YOUR_PASSWORD]
set interfaces pppoe pppoe0 source-interface [YOUR_ETHERNET_INTERFACE]
set interfaces pppoe pppoe0 default-route auto
set interfaces pppoe pppoe0 mtu 1492
set interfaces pppoe pppoe0 description WAN-Interface
commit; save
```

```shell {filename="Static IP"}
set interfaces ethernet [YOUR_ETHERNET_INTERFACE] description WAN-Interface
set interfaces ethernet [YOUR_ETHERNET_INTERFACE] address [YOUR_STATIC_IP]/[PREFIX_LENGTH]
set interfaces ethernet [YOUR_ETHERNET_INTERFACE] mtu 1500
set protocols static route 0.0.0.0/0 next-hop [YOUR_GATEWAY_IP]
set system name-server [PRIMARY_DNS]
set system name-server [SECONDARY_DNS]
commit; save
``` 

After the commit we can check if the routing table is correct. There should be a at least an 0.0.0.0 route in the table.

```shell
admin@BR01# run show ip route
Codes: K - kernel route, C - connected, L - local, S - static,
       R - RIP, O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, F - PBR,
       f - OpenFabric, t - Table-Direct,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup
       t - trapped, o - offload failure

S>* 0.0.0.0/0 [210/0] via 85.146.118.xx, eth1.300, weight 1, 00:00:16
C>* 85.146.118.xx/25 is directly connected, eth1.300, weight 1, 00:00:17
K * 85.146.118.xx/25 [0/0] is directly connected, eth1.300, weight 1, 00:00:17
L>* 85.146.118.xx/32 is directly connected, eth1.300, weight 1, 00:00:17
C>* 192.168.1.0/24 is directly connected, br0, weight 1, 00:07:15
L>* 192.168.1.1/32 is directly connected, br0, weight 1, 00:07:15
```

## Firewall

In VyOS (and most firewall systems using Netfilter/iptables), traffic filtering is managed through three main chains: INPUT, OUTPUT, and FORWARD. Understanding these chains is crucial for configuring firewall rules effectively.

### Input Chain

This controls incoming traffic destined for the VyOS router itself. For example, SSH access to the router or web management interfaces would be filtered by the INPUT chain.

```shell
set firewall ipv4 input filter rule 10 action 'accept'
set firewall ipv4 input filter rule 10 state 'established'
set firewall ipv4 input filter rule 10 state 'related'
set firewall ipv4 input filter rule 10 inbound-interface name [YOUR_INTERFACE]
set firewall ipv4 input filter rule 10 description 'Allow Return traffic destined to the router'
set firewall ipv4 input filter rule 1000 action 'accept'
set firewall ipv4 input filter rule 1000 description 'Allow all traffic from LAN interface'
set firewall ipv4 input filter rule 1000 inbound-interface name br0
set firewall ipv4 input filter default-action drop
commit; save
```

### Output Chain

This manages traffic originating from the VyOS router. If the router itself makes outbound requests (such as NTP synchronization or software updates), they are processed through the OUTPUT chain.

```shell
set firewall ipv4 output filter default-action accept 
commit; save
```

### Forward Chain

This handles traffic passing through the router but not directed to or from it. If VyOS is acting as a router between networks, the FORWARD chain determines which packets are allowed to pass between them.

```shell
set firewall ipv4 forward filter rule 20 action 'accept'
set firewall ipv4 forward filter rule 20 description 'Allow Return traffic through the router'
set firewall ipv4 forward filter rule 20 state 'established'
set firewall ipv4 forward filter rule 20 state 'related'
set firewall ipv4 forward filter rule 20 inbound-interface name [YOUR_INTERFACE]
set firewall ipv4 forward filter rule 1000 action 'accept'
set firewall ipv4 forward filter rule 1000 description 'Allow all traffic from LAN interface'
set firewall ipv4 forward filter rule 1000 inbound-interface name br0
set firewall ipv4 forward filter default-action drop
commit; save
```

## DNS

By default, VyOS doesn't function as a DNS proxy. To enable DNS forwarding from client devices to your upstream DNS servers, you'll need to configure the following settings:

```shell
set service dns forwarding allow-from '192.168.1.0/24'
set service dns forwarding listen-address '192.168.1.1'
set service dns forwarding system
set system name-server [YOUR_INTERFACE]
commit; save
```

This configuration:

- Allows DNS requests from devices in the 192.168.1.0/24 subnet
- Sets your VyOS router (192.168.1.1) as the listening address for DNS requests
- Enables system-wide DNS forwarding
- Forwards requests to your specified upstream DNS server

Remember to replace [YOUR_UPSTREAM_DNS_SERVER] with the actual IP address of your preferred DNS server.

## NAT

We’ll now set up a NAT rule to translate all outgoing traffic from your local network to your public IP address. This will enable devices in your homelab to access the internet using the router’s public IP, ensuring proper routing and security for all outgoing connections.

```shell
set nat source rule 10 description 'Enable NAT on WAN-Interface'
set nat source rule 10 outbound-interface name [YOUR_INTERFACE]
set nat source rule 10 translation address 'masquerade'
commit; save
```
## System 

### Hostname

It’s a good idea to set the Hostname of the system to something that is easily identifiable. I will call mine <kbd>BR01</kbd>

```shell
set system host-name BR01
commit; save
```

### NTP

By default, VyOS acts as an NTP server for clients. This is usually unnecessary for home use, so it's best to disable it.

```shell
delete service ntp allow-client
commit; save
```

VyOS defaults to NTP servers in the US, Germany, and Singapore (AWS). For better accuracy, use servers closer to your location. I’ll be using NL-based servers from pool.ntp.org since I’m located in the Netherlands.

```shell
delete service ntp server time1.vyos.net
delete service ntp server time2.vyos.net
delete service ntp server time3.vyos.net
set service ntp server 0.nl.pool.ntp.org
set service ntp server 1.nl.pool.ntp.org
set service ntp server 2.nl.pool.ntp.org
set service ntp server 3.nl.pool.ntp.org
set system time-zone Europe/Amsterdam
commit; save
```

### User

For security best practices, it's recommended to remove the default <kbd>vyos</kbd> user and create a new one with administrative privileges. Even thought the command suggest that the password will be saved in plaintext, when committing the changes the system will encrypt it by default. 

```shell
set system login user admin authentication plaintext-password admin
commit; save
```

change <kbd>admin</kbd> to your username and password.

Now login with your new user account to make sure everything works. After that delete the <kbd>vyos</kbd> user account.

```shell
delete system login user vyos 
commit; save
```

Now your VyOS router is fully configured and ready to power your homelab! 🎉 With a secure and efficient network in place, you can focus on building and exploring your homelab projects. Happy networking! 🤝