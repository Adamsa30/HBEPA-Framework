# HBEPA Suite Production Server Security Hardening Specification

This document details the configuration baselines, unprivileged service setups, and host-level security profiles required to secure the HBEPA core runtime execution node.

---

## 👥 1. Unprivileged System Account Segregation

To mitigate the risk of arbitrary code execution exploits, all core scripts and database cron daemons must execute exclusively under an unprivileged system service user context with interactive shell options hard-blocked.

```bash
# Initialize a dedicated, unprivileged system service group
sudo groupadd --system hbepa

# Construct the localized system daemon user anchor
sudo useradd --system \
  --gid hbepa \
  --no-create-home \
  --home-dir /opt/hbepa \
  --shell /usr/sbin/nologin \
  hbepa
```

---

## 🔒 2. Filesystem DAC & Privilege Restricting

Apply strict Discretionary Access Control (DAC) modifications over the framework runtime trees to prevent unauthorized modification or data leakage.

```bash
# Secure the core code repository layout zone
sudo chown -R root:hbepa /opt/hbepa/core
sudo chmod 750 /opt/hbepa/core

# Force restrictive permissions directly on individual script files
sudo chmod 640 /opt/hbepa/core/*.py
sudo chmod 750 /opt/hbepa/core/simulate_end_to_end_session.sh

# Establish isolated log write targets for unprivileged daemons
sudo chown -R hbepa:hbepa /var/log/hbepa
sudo chmod 730 /var/log/hbepa
```

---

## 🗃️ 3. Isolated PostgreSQL Sandbox Configuration

Harden the backend database cluster routing properties by adjusting the main configuration file settings (`postgresql.conf`):

```ini
# Enforce strict local loopback address binding limits
listen_addresses = '127.0.0.1'

# Explicitly drop unencrypted cross-network connection vectors
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
```

Enforce strong, cryptographic role mapping via the local authentication control registry file (`pg_hba.conf`):

```text
# TYPE  DATABASE        USER              ADDRESS                 METHOD
host    hbepa_sandbox   hbepa_cron_daemon 127.0.0.1/32            scram-sha-256
host    hbepa_sandbox   hbepa_audit_user  127.0.0.1/32            scram-sha-256
host    all             all               0.0.0.0/0               reject
```

---

## 🚦 4. Host-Level Network Access Control (UFW / Netfilter)

Configure the localized Linux Uncomplicated Firewall (UFW) to enforce strict network isolation boundaries around the container layer:

```bash
# Reset network filtering properties to drop all inbound traffic defaults
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permit mTLS 1.3 incoming traffic specifically on the API gateway container port
sudo ufw allow 443/tcp comment 'HBEPA mTLS Ingress Gateway Proxy'

# Hard-block outside access attempts on the default database listener port
sudo ufw deny 5432/tcp comment 'Block External PostgreSQL Intercept Traps'

# Enable the updated network security ruleset
sudo ufw enable
```
