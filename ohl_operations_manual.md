# HBEPA Standard Operating Procedure (SOP): Occupational Health Liaison Manual
## Section: Manual Exception Logging and Fallback Procedures for Gate 4 Sync Failures

This operational guidebook dictates the protocol for the *Occupational Health Liaison (OHL)* when an automated background Mutual TLS (mTLS 1.3) token synchronization fails to resolve with regional clinical provider networks.

---

## 1. Role Boundaries & Privacy Guardrails

The OHL operates as the single structural bridge between external healthcare diagnostics and the internal corporate HRIS sandbox. 

*   **Absolute Privacy Directive:** The OHL is strictly prohibited from transcribing, uploading, or detailing raw clinical diagnostics, medical terms, or health conditions into the corporate HRIS ledger or ticketing systems.
*   **Role Isolation:** The OHL acts independently of line supervisors and operations directors. Under no circumstances may an OHL disclose an employee's underlying health context to their direct management structure.

---

## 2. Exception Logging Logic & Workflow

If the background automated cron task fails to receive a binary indicator string 14 days prior to a block expiration, and a user falls into the *14-Day Administrative Grace Window*, the OHL must execute the following fallback manual validation sequence:

```text
[Automated Sync Fails] ➔ [14-Day Grace Activated] ➔ [OHL Initiates Secure Manual Verification]
                                                                │
  ┌─────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────┐
  ▼                                                                                                                           ▼
[Option A: Clinical Documentation Clears]                                                   [Option B: Non-Resolution / Timeout]
  │                                                                                                                           │
  ├─ 1. Access Secure Air-Gapped Health Terminal.                                             ├─ 1. Log Token Status as 'EXPIRED'.
  ├─ 2. Confirm receipt of verified clinic notice.                                             ├─ 2. System transitions to 'PAUSED'.
  ├─ 3. Match against user hash token.                                                        └─ 3. Enforce Strict Non-Separation Clause.
  └─ 4. Set DB flag: 'CONSUMED' / op_verified = 1.
```

### Protocol A: Clinical Verification Clears Electronically / Physically
When a verified clinical confirmation (e.g., from an authorized provider network such as IU Health Primary Care) arrives via an air-gapped secure link or signed physical mailroom intake, the OHL shall:
1. Log into the secure, isolated health terminal module (completely segregated from general corporate operational views).
2. Enter the designated `token_id` matching the employee's anonymized transaction profile.
3. Manually assert the verified functional barrier status *without adding text descriptions of symptoms or constraints*.
4. Commit the manual query update to the ledger schema. The script will automatically trigger a downstream API write setting `token_status = 'CONSUMED'` and `op_verified = 1`, refreshing the employee's accommodation block for a standard consecutive 90-day cycle.

### Protocol B: Handling Non-Resolution or Expiration Timeouts
If the 14-day administrative grace window expires without incoming validation data from the participant or provider, the OHL must execute the following safety protocol:
1. Log the transaction token status as `EXPIRED`. The HRIS ledger will programmatically pause active remote network tracking log cycles for that user hash.
2. **Enforce the Statutory Non-Separation Clause:** The OHL must flag the file to prevent the system from generating an automated termination notice. The system must lock the record to ensure the employee remains on inactive, protected retention status while a human-led interactive reasonable accommodation dialogue is formally scheduled.

---

```text
This is for informational purposes only. For medical advice or diagnosis, consult a professional. AI responses may include mistakes.
```
