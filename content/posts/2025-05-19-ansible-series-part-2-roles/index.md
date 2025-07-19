---
title: Ansible Series Part 2 | Playbooks, Roles & Handlers
description: Learn to organize your Ansible automation with playbooks, roles, and handlers for cleaner, scalable infrastructure.
date: 2025-05-19
draft: false
categories:
  - Automation
tags:
  - ansible
cover: cover.jpg
---

In this part of the Ansible series, you’ll learn how to automate routine system maintenance tasks like updating packages and rebooting, while organizing your project using **roles** and **handlers** for better structure and reuse.

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

They’re usually used for things like restarting services or rebooting after updates.

Example:
```yaml
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

So if the package update changes something, the handler will run. Otherwise, it won’t.

## Directory Structure

```bash
homelab-ansible/
├── ansible.cfg
├── inventory/
│   └── hosts.yml
├── playbooks/
│   └── system-maintenance.yml
├── roles/
│   └── maintenance/
│       ├── tasks/
│       │   └── main.yml
│       └── handlers/
│           └── main.yml
└── README.md
```

## Create a Maintaince role

To maintain a well-organized and reusable Ansible project, we've introduced a role called <kbd>maintenance</kbd> that handles system package updates across all hosts. By using roles, we can group related tasks and logic—in this case, routine system maintenance—into a dedicated, structured directory for better clarity and reusability.

### Create Task

```yaml
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

```yaml
- name: Reboot if required
  ansible.builtin.reboot:
    reboot_timeout: 600
```

The reboot handler is triggered only when notified by the upgrade task. If changes are made during the upgrade, the handler will automatically reboot the host to apply updates that require a restart.

## Create Playbook

```yaml
- name: Perform system maintenance
  hosts: homelab
  become: true
  roles:
    - maintenance
```


This playbook:
- Targets the <kbd>homelab</kbd> group in your <kbd>hosts.yml</kbd>
- Uses privilege escalation (<kbd>become: true</kbd>)
- Calls the <kbd>maintenance</kbd> role


## Run the Playbook

From your project root:

```bash
ansible-playbook playbooks/system-maintenance.yml --ask-become-pass
```

If your user has passwordless sudo, you can skip the <kbd>--ask-become-pass</kbd> flag.

## Why This Structure Works

This role-based layout keeps your playbooks clean and modular:

- **Separation of concerns:** Logic for package maintenance is kept inside a role
- **Reusability:** You can reuse the <kbd>maintenance</kbd> role in other playbooks or environments
- **Cleaner playbooks:** Top-level playbooks become short and easy to understand

## Recap

You’ve now:

- Created a system maintenance role
- Used handlers to reboot only when needed
- Organized your playbook for better scalability

Next up: using **Ansible Vault** to manage secrets securely!

> In the meantime check out my [git repro](https://github.com/svenvg93/ansible-homelab) that I use for my homelab
