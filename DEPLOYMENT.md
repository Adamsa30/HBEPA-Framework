# HBEPA Production Infrastructure Deployment Guide (DEPLOYMENT.md)

This deployment blueprint details the systems architecture configuration, directory layouts, environment initialization tasks, and systemd service runtime parameters required to host the Home-Based Employment Preservation Accommodation (HBEPA) reference suite on an isolated enterprise Linux server.

---

## 🏗️ 1. Reference Architecture Overview

The production runtime environment decouples public network ingress points from core relational storage layers via an encrypted, multi-layered layout:

### Server Hardening Baseline Constraints
* **Operating System Target:** Ubuntu 22.04 LTS or RHEL 9 (Minimal installation profile).
* **Network Isolation:** The database instance must bind strictly to the local loopback interface (`127.0.0.1`) or sit inside a dedicated Private Virtual Cloud (VPC) subnet block behind an adaptive firewall proxy layer.

---

## 📂 2. Enterprise System Directory Layout

Execute the following commands under root administrative privileges to provision isolated project execution environments, load environment configurations, and initialize the system certificate directory boundaries:

```bash
# Initialize core enterprise runtime system root trees
mkdir -p /opt/hbepa/core
mkdir -p /opt/hbepa/bin
mkdir -p /var/log/hbepa

# Provision separate cryptographic storage boundaries for mTLS certificate validation
mkdir -p /etc/hbepa/certs
chmod 700 /etc/hbepa/certs

# Create an unprivileged system service group and account user anchor
groupadd --system hbepa
useradd --system \
    --gid hbepa \
    --no-create-home \
    --home-dir /opt/hbepa \
    --shell /usr/sbin/nologin \
    hbepa

# Transfer secure ownership configurations across operational file zones
chown -R hbepa:hbepa /opt/hbepa
chown -R hbepa:hbepa /var/log/hbepa
```

---

## 🗄️ 3. Isolated PostgreSQL Sandbox Provisioning

1. Log into your production database instance as a cluster superuser and initialize the tracking database, unprivileged user permissions mapping, and schema structure templates:

```sql
-- Allocate an isolated relational cluster workspace
CREATE DATABASE hbepa_sandbox;

-- Establish a dedicated, restricted service account user target
CREATE USER hbepa_cron_daemon WITH PASSWORD 'SecureDaemonPassword789!';
CREATE USER hbepa_audit_user WITH PASSWORD 'SecureSandboxPassword123!';

-- Connect to the isolated sandbox database to authorize structural grants
\c hbepa_sandbox;

-- Enable the standard cryptographic indexing extension template layer
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

2. Execute your active repository file layout script to construct database constraints, hash tables, and structural anti-tampering ledger rules natively:
```bash
psql -h localhost -U postgres -d hbepa_sandbox -f database_schema.sql
```

---

## ⚙️ 4. Systemd Background Daemon Integration

To securely operationalize the mock clinical callback validator and background lifecycle daemons as unprivileged Linux system background unit tasks, register the following service layout specifications:

### Service Configuration A: Edge Data Firewall Middleware (`/etc/systemd/system/hbepa-callback.service`)
```ini
[Unit]
Description=HBEPA Edge Data Firewall Clinical Callback Server
After=network.target postgresql.service
Documentation=https://github.com

[Service]
Type=simple
User=hbepa
Group=hbepa
WorkingDirectory=/opt/hbepa/core
ExecStart=/usr/bin/python3 /opt/hbepa/core/mock_clinical_callback_server.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
StandardOutput=append:/var/log/hbepa/firewall_stdout.log
StandardError=append:/var/log/hbepa/firewall_stderr.log

# Sandbox system hardening directives
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
CapabilityBoundingSet=~CAP_SYS_ADMIN

[Install]
WantedBy=multi-user.target
```

### Service Configuration B: Cron Daemon Lifecycle Orchestrator (`/etc/cron.d/hbepa-lifecycle-daemon`)
To run the 30/60/90-day block recertification sweep automatically every hour to evaluate remaining block durations and activate the 14-day administrative grace protection buffers, add this entry to the system cron tab layout:

```text
0 * * * * hbepa /usr/bin/python3 /opt/hbepa/core/gate4_recertification_daemon.py >> /var/log/hbepa/lifecycle_cron.log 2>&1
```

---

## 🚀 5. Core Environment Runtime Initialization

Following structural file placement of your Python automations (`mock_clinical_callback_server.py`, `gate4_recertification_daemon.py`, and `process_hbepa_disconnect_handler.py`) into `/opt/hbepa/core/`, invoke the final system configuration task sequences:

```bash
# Apply strict access privilege restrictions on runtime code scripts
chmod 640 /opt/hbepa/core/*.py
chown -R hbepa:hbepa /opt/hbepa/core

# Reload systemd system configuration graphs to map new unit tasks
systemctl daemon-reload

# Activate, start, and audit your background clinical data firewall service
systemctl enable --now hbepa-callback.service
systemctl status hbepa-callback.service

# Run your committed shell utility script to verify structural system integration metrics
chmod +x simulate_end_to_end_session.sh
./simulate_end_to_end_session.sh
```
