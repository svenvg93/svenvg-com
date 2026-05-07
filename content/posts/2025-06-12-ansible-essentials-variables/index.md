---
title: "Ansible Essentials: Variables & Facts"
description: Learn how Ansible variables and facts work — from host_vars and group_vars to gathered system facts — and use them to write smarter, host-aware playbooks.
date: 2025-06-12
draft: false
categories:
  - Automation
tags:
  - ansible
cover: cover.svg
series:
  - Ansible Essentials
series_order: 5
---

Instead of hardcoding values in every task, you define variables once and reference them everywhere. **Facts** go further — Ansible automatically discovers information about each host that you can use without defining anything manually.

## Variable Sources

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

## Recap

You've now covered:

- Defining variables in `group_vars` and `host_vars`
- Using gathered facts like `ansible_os_family` for host-aware tasks
- Capturing task output with `register`
- Inspecting variables with `debug`
