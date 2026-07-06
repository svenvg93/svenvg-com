---
title: "Ansible Essentials: Variables, Facts & Templates"
description: Learn how Ansible variables and facts work — from group_vars and host_vars to gathered system facts — then use Jinja2 templates to project them into dynamic, host-aware configuration files.
date: 2025-06-05
draft: false
categories:
  - Automation
tags:
  - ansible
cover: cover.svg
series:
  - Ansible Essentials
series_order: 2
aliases:
  - /posts/2025-06-12-ansible-essentials-variables/
  - /posts/ansible-essentials-jinja2-templates/
---

Instead of hardcoding values in every task, you define variables once and reference them everywhere. **Facts** go further — Ansible automatically discovers information about each host that you can use without defining anything manually. Once you have variables and facts to work with, **Jinja2 templates** let you project them into config files — instead of maintaining ten nearly identical files by hand, you write a single file with placeholders that Ansible fills in per host at deploy time.

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

## Recap

You've now covered:

- Defining variables in `group_vars` and `host_vars`
- Using gathered facts like `ansible_os_family` for host-aware tasks
- Capturing task output with `register`
- Inspecting variables with `debug`
- Writing `.j2` templates using `{{ }}`, `{% if %}`, and `{% for %}` syntax
- Placing templates inside a role's `templates/` directory
- Deploying rendered files with the `template` module

Next up: **Managing Secrets with Vault** — how to keep passwords and API keys out of version control while still using them in your playbooks.
