# HBEPA Architecture Specification: Relational Database Data Dictionary

This document provides the definitive data dictionary for the PostgreSQL tables tracking anonymized transaction tokens and payroll ledgers within the isolated HRIS sandbox environment.

---

## 1. Table: `hbepa_tokens`
Tracks the lifecycle, generation, and validation status of ephemeral mTLS 1.3 cryptographic handshake tokens.

| Column Name | Data Type | Constraints | Operational & Privacy Purpose |
| :--- | :--- | :--- | :--- |
| `token_id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Provides a globally unique, non-sequential system identifier for each transaction to avoid enumeration vulnerabilities. |
| `anonymized_user_hash` | VARCHAR(64) | NOT NULL | Stores the SHA-256 hash of the unique employee identifier, preventing general system administrators from matching clinical metrics to physical names. |
| `ephemeral_handshake_token` | VARCHAR(128) | UNIQUE, NOT NULL | Holds the short-lived, single-use token transmitted to external clinical data brokers via encrypted mTLS tunnels. |
| `issued_at` | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Logs the precise timestamp of token issuance, initializing the 90-day tracking lifecycle block. |
| `expires_at` | TIMESTAMPTZ | NOT NULL | Establishes the hard system cutoff matching the end of the 14-day administrative grace period. |
| `token_status` | VARCHAR(20) | CHECK (IN ('PENDING', 'CONSUMED', 'EXPIRED')) | Programmatically routes lifecycle steps: `PENDING` during grace periods, `CONSUMED` upon validation, or `EXPIRED` if timeouts occur. |

---

## 2. Table: `hbepa_payroll_ledger`
Logs verified remote presence session hours under the protected labor classification code.

| Column Name | Data Type | Constraints | Operational & Privacy Purpose |
| :--- | :--- | :--- | :--- |
| `entry_id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique ledger tracking sequence ID for independent corporate wage-and-hour audits. |
| `anonymized_user_hash` | VARCHAR(64) | NOT NULL, REFERENCES hbepa_tokens | Relational foreign key tying attendance metrics strictly to an anonymized user profile. |
| `pay_period_start` | DATE | NOT NULL | Records the start date of the active corporate tracking cycle. |
| `pay_period_end` | DATE | NOT NULL | Records the end date of the active corporate tracking cycle. |
| `labor_code` | VARCHAR(50) | DEFAULT 'Approved Employment Preservation Accommodation Time' | Hardcodes the immutable labor string to shield the entry from being mixed with production metrics. |
| `session_persistence_hours`| NUMERIC(5,2)| NOT NULL | Quantifies the exact network tunnel longevity logs captured via the Gate 2 VPN tunnel. |
| `op_verified_state` | BOOLEAN | NOT NULL, DEFAULT FALSE | Receives the flat binary pass from the data firewall filter indicating validation clearance. |
| `is_locked_for_audit` | BOOLEAN | DEFAULT TRUE | Programmatically prevents retrospective manipulation of attendance states by line supervisors. |

---

```text
This is for informational purposes only. For medical advice or diagnosis, consult a professional. AI responses may include mistakes.
```
