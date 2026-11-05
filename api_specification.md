# HBEPA Reference Architecture: Backend API Endpoints (TRD)

This specification defines the endpoints used by the background `Status Sync Daemon` during Gate 4 compliance updates. All traffic requires an established Mutual TLS (mTLS 1.3) handshake using certified client certificates.

---

## 1. Token Generation Endpoint

*   **Endpoint Path:** `POST /api/v1/gate4/tokens/issue`
*   **Access Control:** Restricted to background automated cron engine system-level credentials.
*   **Purpose:** Issues a short-lived, anonymized transaction token 14 days prior to block expiration.

### A. Request Payload Layout (JSON)
```json
{
  "anonymized_user_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "requested_lifecycle_block_days": 90,
  "client_routing_zone": "IN-HENDRICKS-AVON"
}
```

### B. Expected Response Payload (201 Created)
```json
{
  "token_id": "8f3b8a32-9c12-4c22-b883-fa8812c32ef8",
  "ephemeral_handshake_token": "hbepa_tok_sec_93810283918239102839123",
  "issued_at": "2026-11-05T07:10:00Z",
  "expires_at": "2026-11-19T07:10:00Z",
  "token_status": "PENDING"
}
```

---

## 2. Clinical Sync Callback Endpoint (Data Firewall)

*   **Endpoint Path:** `POST /api/v1/gate4/tokens/validate-sync`
*   **Access Control:** Restricted to verified external regional provider endpoints (e.g., Authorized IU Health Health-Liaison Broker).
*   **Purpose:** Receives validation confirmations. The incoming data payload is passed through deep packet inspection to strip text diagnostics, updating the core HRIS using a flat binary format.

### A. Request Payload Layout From Provider Network (JSON)
```json
{
  "ephemeral_handshake_token": "hbepa_tok_sec_93810283918239102839123",
  "provider_validation_payload": {
    "functional_transportation_barrier_confirmed": true,
    "acute_task_impairment_status": "ACTIVE_STABLE",
    "clinical_diagnostic_notes_redacted": "[ENFORCED_HIPAA_DATA_STRIP_RULE]"
  }
}
```

### B. Internal Sanitized HRIS Database Write (Post-Firewall Filter)
```json
{
  "token_id": "8f3b8a32-9c12-4c22-b883-fa8812c32ef8",
  "token_status": "CONSUMED",
  "op_verified": 1
}
```

---

```text
This is for informational purposes only. For medical advice or diagnosis, consult a professional. AI responses may include mistakes.
```
