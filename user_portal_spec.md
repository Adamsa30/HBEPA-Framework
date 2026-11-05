# HBEPA System Architecture: User Self-Service Portal Specifications

This specification details the user-interface boundaries, onboarding workflows, and cryptographic authentication binding protocols for the employee-facing self-service dashboard.

---

## 1. Secure Onboarding & Token Binding Protocol

The initial registration pipeline establishes hardware-backed presence verification metrics while preventing geographic telemetry leaks.

### Step 1: Initial Identity Verification
*   The user authenticates via the primary enterprise Identity Provider (IdP) using standard corporate multi-factor credentials.
*   The system cross-references the user's randomized database row to confirm an approved **Gate 1** binary activation string (`{"op_verified": 1}`).

### Step 2: FIDO2 / WebAuthn Hardware Binding
*   The portal prompts the user to register an authorized hardware security key (e.g., a physical FIDO2 token).
*   The web browser triggers a native `navigator.credentials.create()` call. 
*   **Privacy Restriction:** The browser client strips device-specific serial hardware numbers, returning exclusively the anonymous public key credential block to the backend database registry.

### Step 3: Proximity Token Calibration (Optional)
*   The portal assists the user in calibrating a designated local device (e.g., smartphone) for short-range Bluetooth Low Energy (BLE) or Ultra-Wideband (UWB) proximity checks.
*   **Privacy Restriction:** The pairing routine utilizes random rolling MAC addresses, programmatically blocking the corporate server from logging fixed hardware identifiers or nearby ambient networks.

---

## 2. Participant Interface Layout (Dashboard View)

The secure user interface provides transparent visibility regarding logging status, active lifecycles, and grace counters without triggering anxiety alerts.

### A. Current Presence State Core Display
*   **Active Banner (Green):** Displays text: *"Secure Connection Verified: Session Persistence Logged under Approved Employment Preservation Accommodation Time."*
*   **Paused Banner (Blue):** Appears when the user manually suspends tracking for medical or self-care breaks. Displays text: *"Session Suspended. Attendance Ledger Paused."*

### B. Fixed Interval Counter
*   Displays a simple countdown metric tracking the current 90-day block allocation.
*   **Grace Alert Interface:** If a Gate 4 automated check enters a `PENDING` state at the 14-day threshold, the dashboard displays **Template 1** (Soft Amber Alert) confirming that the *Administrative Grace Window* is actively shielding the profile, providing direct communication links to the Occupational Health Liaison.

---

```text
This is for informational purposes only. For medical advice or diagnosis, consult a professional. AI responses may include mistakes.
```
