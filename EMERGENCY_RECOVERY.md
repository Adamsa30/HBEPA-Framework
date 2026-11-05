# HBEPA Suite Operational Emergency Recovery Plan

This specification details standard operating procedures, fail-safe overrides, and data recovery workflows for the HBEPA platform during catastrophic core infrastructure collapses.

---

## 🚦 1. Crisis Classification & Initial Assessment

To prevent administrative chaos or accidental payroll logging drops, system outages must be mapped against three explicit tier boundaries:

| Outage Classification Tier | Impacted Infrastructure | Automatic Fail-Safe State | Required Action |
| :--- | :--- | :--- | :--- |
| **Tier I: Local Disconnect** | Local Client Terminal Node Drop | Local Microsecond Save Loop | Automatic recovery handled via `process_hbepa_disconnect_handler.py`. |
| **Tier II: Sync Bridge Drop** | API Gateway mTLS Provider Proxy Outage | Local 14-Day Administrative Grace | System locks active data fields. Daemon shields user profile from separation. |
| **Tier III: Database Outage** | Primary PostgreSQL Cluster Corruption | Standby Read-Only Failover Loop | Manual switch to secondary hot-standby node required. |

---

## 🛡️ 2. Tier II Outage: Provider Network Failure Recovery Runbook

If an extended external healthcare network collapse occurs, blocking the automated 30/60/90-day background validation sweeps, administrators must execute these steps to ensure continuous safe harbor compliance.

### Phase A: Engaging the Safe Harbor Lock
1. **Verify Automatic Grace Intercept:** Confirm that `gate4_recertification_daemon.py` has shifted the impacted user hash blocks into an amber state: `INITIATE_ADMINISTRATIVE_GRACE_PERIOD`.
2. **Prevent Line Manager Tampering:** Ensure that front-end supervisor view boundaries continue to display a generic `Active/Idle` status loop to enforce total supervisory blindness during the outage window.

### Phase B: Manual Clinical Token Attestation
If the provider gateway remains completely unreachable beyond the 14-day grace window, the air-gapped **Occupational Health Liaison (OHL)** must switch to manual clinical validation:

```text
[External Secure Fax / Encrypted Mail Intake]
                     │
                     ▼
[OHL Verification: Check Provider Signature]
                     │
                     ▼
[Execute SQL Token Regeneration Bypass Code]
```

---

## ⚙️ 3. Emergency Administrative Core Override Procedures

To prevent a hard expiration lock-out during a Tier II/III recovery scenario, an authorized database administrator can execute a manual token extension query to preserve payroll logging.

### Execute Manual Extension Block Command:
Connect directly to the private PostgreSQL loopback instance via an authorized terminal session:

```sql
-- Securely push back the expiration boundary for the targeted hash index
UPDATE hbepa_tokens 
SET token_status = 'PENDING', 
    expires_at = CURRENT_TIMESTAMP + INTERVAL '30 day'
WHERE anonymized_user_hash = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
AND token_status = 'EXPIRED';
```

*Note: This command forces an explicit 30-day administrative block extension, allowing continuous workforce tracking while the core clinical API gateway infrastructure is safely restored.*
