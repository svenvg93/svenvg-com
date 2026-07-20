---
title: "Ansible: Playbooks, Roles, Templates & Vault"
description: Install Ansible and organize your automation into playbooks, roles, and handlers, use variables, facts, and Jinja2 templates to generate host-aware configuration, and encrypt secrets like API keys with Ansible Vault.
date: 2025-05-15
draft: false
cover: cover.svg
categories:
  - Automation
tags:
  - ansible
---

Ansible is a powerful automation tool that lets you manage your infrastructure using simple, repeatable playbooks. This post walks through the full arc of getting productive with it: installing Ansible and configuring SSH access, organizing your automation into playbooks, roles, and handlers, using variables and gathered facts to keep configuration host-aware, projecting that data into files with Jinja2 templates, and finally encrypting secrets like API keys with Ansible Vault so they never end up in version control.

## Install Ansible

Install Ansible on your local workstation or control node. In my case I use a my macbook as "control node".

Ensure pip is available and up to date:
```bash
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip
```

Install Ansible:
```bash
pip install ansible
```

Verify the installation:
```bash
ansible --version
```

## Set Up SSH Key Access

Ansible connects to remote machines via SSH. To avoid typing passwords every time, set up SSH key authentication.

If you already use [Tailscale][1] to access your nodes, you can use **Tailscale SSH** instead of managing your own SSH keys.


### Generate a key pair

```bash
ssh-keygen -t ed25519
```

Press enter to use the default file location. Leave the passphrase empty for automation.

### Copy your public key to a remote host

```bash
ssh-copy-id user@your-server-ip
```

Then test your connection:

```bash
ssh user@your-server-ip
```

If you’re logged in without a password prompt, you're ready to automate.

## Project Structure

Here's how a fully organized Ansible project ends up looking once you're using roles, host-aware variables, and Vault-protected secrets:

```bash
homelab-ansible/
├── ansible.cfg
├── inventory/
│   └── hosts.yml
├── group_vars/
│   ├── all.yml
│   └── vault.yml
├── host_vars/
│   └── web01.yml
├── playbooks/
│   ├── system-maintenance.yml
│   └── monitoring.yml
├── roles/
│   ├── maintenance/
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── handlers/
│   │       └── main.yml
│   └── monitoring/
│       ├── tasks/
│       │   └── main.yml
│       └── templates/
│           └── prometheus-targets.j2
└── README.md
```

Let's build this up piece by piece, starting with the configuration file and inventory.

### Create the Ansible configuration file

The `ansible.cfg` file is typically located either in your home directory or in the `/etc/ansible` directory.

```ini
[defaults]
inventory = ./inventory/hosts.yml
host_key_checking = False
retry_files_enabled = False
timeout = 10
```

This configuration:
- Points to your inventory file
- Disables SSH host key prompts
- Improves reliability by disabling retry files and adding a timeout

### Define Your Inventory

Create a static inventory file to list your homelab machines. This file is typically placed in your current working directory, alongside your playbooks and roles in the inventory folder

```yaml
all:
  homelab:
    hosts:
      server01:
      server02:
```

Replace `server01` and `server02` with actual IPs or hostnames.

## Test SSH Connectivity

Use Ansible's ping module to confirm everything is working:

```bash
ansible -m ping homelab
```

Each machine should return `pong` if SSH and the inventory are set up correctly. With connectivity confirmed, you're ready to organize real automation tasks using playbooks, roles, and handlers.

## What Are Ansible Roles?

Roles are a way to organize your Ansible code into reusable, modular components.

A role has a standard folder structure (tasks/, handlers/ etc.), and can include everything needed to configure a specific part of your system.

Benefits:
- Keeps your playbooks clean
- Promotes reuse across multiple playbooks
- Encourages good organization

Example:
Instead of writing all tasks inline, you just do:

```yaml
roles:
  - maintenance
```

And Ansible will run roles/maintenance/tasks/main.yml.

## What Are Handlers?

Handlers are special tasks triggered only when notified by another task.

They're usually used for things like restarting services or rebooting after updates.

Example:
```yaml {filename="main.yml"}
tasks:
  - name: Update packages
    apt:
      upgrade: dist
    notify: Reboot if required

handlers:
  - name: Reboot if required
    reboot:
      reboot_timeout: 600
```

So if the package update changes something, the handler will run. Otherwise, it won't.

## Create a Maintenance role

To maintain a well-organized and reusable Ansible project, we've introduced a role called `maintenance` that handles system package updates across all hosts. By using roles, we can group related tasks and logic—in this case, routine system maintenance—into a dedicated, structured directory for better clarity and reusability.

### Create Task

```yaml {filename="main.yml"}
- name: Update APT package cache
  ansible.builtin.apt:
    update_cache: true
    cache_valid_time: 3600

- name: Upgrade all packages
  ansible.builtin.apt:
    upgrade: dist
    autoremove: true
    autoclean: true
  notify: Reboot if required
```


This file defines the main tasks:
- Updates the APT cache
- Upgrades all packages
- Notifies the reboot handler if anything changes

### Create Handlers

```yaml {filename="main.yml"}
- name: Reboot if required
  ansible.builtin.reboot:
    reboot_timeout: 600
```

The reboot handler is triggered only when notified by the upgrade task. If changes are made during the upgrade, the handler will automatically reboot the host to apply updates that require a restart.

## Create Playbook

```yaml {filename="system-maintenance.yml"}
- name: Perform system maintenance
  hosts: homelab
  become: true
  roles:
    - maintenance
```


This playbook:
- Targets the `homelab` group in your `hosts.yml`
- Uses privilege escalation (`become: true`)
- Calls the `maintenance` role


## Run the Playbook

From your project root:

```bash
ansible-playbook playbooks/system-maintenance.yml --ask-become-pass
```

If your user has passwordless sudo, you can skip the `--ask-become-pass` flag.

## Variable Sources

Instead of hardcoding values in every task, you define variables once and reference them everywhere. **Facts** go further — Ansible automatically discovers information about each host that you can use without defining anything manually.

| Source | Scope | Example use |
|--------|-------|-------------|
| `group_vars/all.yml` | All hosts | NTP server, DNS |
| `group_vars/<group>.yml` | Hosts in a group | Subnet per VLAN |
| `host_vars/<host>.yml` | Single host | Per-host port |
| Playbook `vars:` | Current play | One-off overrides |

`host_vars` overrides `group_vars`, which overrides `all`. Playbook `vars:` overrides all of these.

## Defining Variables

```bash
homelab-ansible/
├── group_vars/
│   ├── all.yml
│   └── servers.yml
└── host_vars/
    └── web01.yml
```

```yaml {filename="group_vars/all.yml"}
ntp_server: "pool.ntp.org"
timezone: "Europe/Amsterdam"
```

```yaml {filename="host_vars/web01.yml"}
http_port: 8080
```

Use them in tasks with `{{ variable_name }}`:

```yaml {filename="tasks/main.yml"}
- name: Set timezone
  community.general.timezone:
    name: "{{ timezone }}"
```

## Ansible Facts

When `gather_facts: true` (the default), Ansible collects system information from the host at the start of each play.

| Fact | Example value |
|------|--------------|
| `ansible_hostname` | `web01` |
| `ansible_default_ipv4.address` | `192.168.1.10` |
| `ansible_distribution` | `Ubuntu` |
| `ansible_os_family` | `Debian` |
| `ansible_memtotal_mb` | `7976` |

To see all available facts for a host:

```bash
ansible web01 -m setup
```

## Using Facts in Tasks

```yaml {filename="tasks/main.yml"}
- name: Install packages (Debian)
  ansible.builtin.apt:
    name: curl
    state: present
  when: ansible_os_family == "Debian"

- name: Install packages (RedHat)
  ansible.builtin.dnf:
    name: curl
    state: present
  when: ansible_os_family == "RedHat"
```

## Registering Task Output

Use `register` to capture a task result and act on it:

```yaml {filename="tasks/main.yml"}
- name: Check if nginx is running
  ansible.builtin.systemd:
    name: nginx
  register: nginx_status
  changed_when: false
  failed_when: false

- name: Start nginx if not running
  ansible.builtin.systemd:
    name: nginx
    state: started
  when: nginx_status.status is defined and nginx_status.status.ActiveState != "active"
```

## The debug Module

Use `debug` to inspect variables while developing:

```yaml
- name: Show host IP
  ansible.builtin.debug:
    msg: "Host IP is {{ ansible_default_ipv4.address }}"

- name: Dump all facts
  ansible.builtin.debug:
    var: ansible_facts
```

Now that you have variables and facts to work with, let's put them to use: projecting them into real configuration files with Jinja2 templates.

## Template Syntax

Templates are plain text files ending in `.j2` with three main expressions:

| Syntax | Purpose |
|--------|---------|
| `{{ variable }}` | Insert a variable value |
| `{% if condition %}` | Conditional block |
| `{% for item in list %}` | Loop |

## Where Templates Live

Place templates inside your role under a `templates/` directory:

```bash
roles/
└── monitoring/
    ├── tasks/
    │   └── main.yml
    └── templates/
        └── prometheus-targets.j2
```

## The template Module

Use `template` instead of `copy` whenever you need variable substitution:

```yaml {filename="tasks/main.yml"}
- name: Deploy Prometheus scrape config
  ansible.builtin.template:
    src: prometheus-targets.j2
    dest: /etc/prometheus/targets.yml
    owner: prometheus
    group: prometheus
    mode: '0644'
  notify: Reload Prometheus
```

## Writing a Template

This template generates a Prometheus scrape config from your inventory:

```jinja2 {filename="prometheus-targets.j2"}
# Managed by Ansible — do not edit manually
scrape_configs:
  - job_name: node_exporter
    static_configs:
      - targets:
{%- for host in groups['homelab'] %}
          - "{{ hostvars[host]['ansible_host'] }}:9100"
{%- endfor %}
```

Add a host to your inventory and the next run updates the config automatically.

Use `{% if %}` to include sections conditionally:

```jinja2
{% if enable_https %}
    scheme: https
    tls_config:
      insecure_skip_verify: true
{% endif %}
```

## Create the Playbook

```yaml {filename="monitoring.yml"}
- name: Deploy monitoring config
  hosts: monitoring_server
  become: true
  roles:
    - monitoring
```

## Run It

```bash
ansible-playbook playbooks/monitoring.yml --ask-become-pass
```

## Managing Secrets with Vault

Storing API keys, tokens, and passwords in your playbooks isn't safe—especially if you keep your Ansible project in version control. That's where **Ansible Vault** comes in. It lets you encrypt sensitive variables while still using them like any other part of your automation.

Now that your playbooks use variables and templates, here's how to keep secrets like API keys out of version control with Vault. In this example, I'll use it to store a Tailscale auth key, which one of my roles uses to authenticate a server into my private Tailscale network.

### Create the Vault File

Create an encrypted file for your secrets:

```bash
ansible-vault create group_vars/vault.yml
```

When the editor opens, enter something like:

```yaml {filename="vault.yml"}
tailscale_auth_key: "tskey-REPLACE_ME"
```

Then save and close the editor. The file is now encrypted and safe to commit (if you're careful with your vault password).

### Use the Vault Variable in a Playbook

You can now use the secret just like any other variable:

```yaml {filename="task.yml"}
---
- name: Check if tailscaled service is running
  ansible.builtin.systemd:
    name: tailscaled
  register: tailscaled_service
  changed_when: false
  failed_when: false

- name: Skip Tailscale Setup
  ansible.builtin.meta: end_host
  when: tailscaled_service.status.ActiveState == "active"

- name: Check if Tailscale is installed
  ansible.builtin.stat:
    path: /usr/sbin/tailscale
  register: tailscale_installed

- name: Download Tailscale install script
  ansible.builtin.get_url:
    url: "{{ tailscale_install_url }}"
    dest: /tmp/tailscale-install.sh
    mode: '0755'
  when: not tailscale_installed.stat.exists

- name: Run Tailscale install script
  ansible.builtin.command: /tmp/tailscale-install.sh
  when: not tailscale_installed.stat.exists
  changed_when: true
  notify: Restart tailscaled

- name: Ensure tailscaled is enabled and started
  ansible.builtin.systemd:
    name: tailscaled
    enabled: true
    state: started

- name: Check Tailscale status
  ansible.builtin.command: tailscale status
  register: tailscale_status
  changed_when: false
  failed_when: false
  when: tailscale_installed.stat.exists

# The Tailscale auth key should be stored in an encrypted vault:
# tailscale_auth_key: "tskey-YOUR_KEY_HERE"

- name: Authenticate with Tailscale if logged out and auth key is provided
  ansible.builtin.command: >
    tailscale up --authkey={{ tailscale_auth_key }}
  when:
    - tailscale_auth_key is defined
    - tailscale_auth_key | length > 0
    - "'Logged out.' in tailscale_status.stdout"
  changed_when: true

- name: Enable Tailscale SSH on the host
  ansible.builtin.command: tailscale up --ssh
  when: tailscale_enable_ssh and tailscale_auth_key is defined and tailscale_installed.stat.exists
  changed_when: true
  tags:
    - tailscale_ssh
```

### Run the Playbook with Vault

In your playbook you need to reference where the vault file can be found.

```yaml {filename="tailscale.yml"}
---
# Enroll hosts into Tailscale network.
- name: Enroll hosts into Tailscale
  hosts: all
  become: true
  vars_files:
    - ../group_vars/vault.yml
  gather_facts: true
  roles:
    - tailscale
```

Once you've encrypted your secrets with Ansible Vault, you can run your playbook securely by providing the vault password at runtime:

```bash
ansible-playbook playbooks/tailscale.yml --ask-vault-pass
```

This command will prompt you for the vault password before executing the playbook, ensuring your secrets are decrypted only when needed.

### Editing or Updating the Vault

To edit your encrypted file later

```bash
ansible-vault edit group_vars/vault.yml
```

To change the vault password

```bash
ansible-vault rekey group_vars/vault.yml
```

### Git Ignore Vault Files

Add this to your `.gitignore` file to prevent secrets from being committed:

```bash
group_vars/vault.yml
```

## Recap

You've now installed Ansible and set up SSH key access, organized a project around `ansible.cfg`, inventory, playbooks, and roles, built a reusable `maintenance` role with a handler, used variables and facts to keep tasks host-aware, generated dynamic configuration with Jinja2 templates, and locked sensitive values away with Ansible Vault — everything you need to run a clean, secure homelab automation setup.

[1]: https://tailscale.com
