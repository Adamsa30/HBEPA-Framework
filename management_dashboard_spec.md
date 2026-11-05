# HBEPA System Design: Management & Payroll Dashboard Specifications

This technical spec defines the interface boundaries for the corporate management portal, strictly enforcing privacy-by-design principles to ensure operational logging without employee surveillance.

---

## 1. Supervisor Interface Constraints (Manager View)

The system restricts supervisor visibility strictly to chronological state indicators. All direct spatial, visual, or contextual tracking arrays are programmatically barred from the user interface.

### A. Permitted UI Status Indicators
*   **Active Status:** Indicates that an employee's hardware security key (FIDO2/WebAuthn) has validated presence and a secure VPN tunnel is maintained.
*   **Idle Status:** Automatically triggered if keyboard/mouse activity pauses for >15 minutes. Logs historical timing without logging active inputs.
*   **Paused Status:** Indicates that the employee has manually paused their session to attend to personal care or medical breaks.

### B. Prohibited Monitoring Vectors (Hard-Coded Blocks)
*   🚫 **Live Video/Webcam Feeds:** Webcam hardware endpoints are decoupled from the authentication package.
*   🚫 **Keystroke Logging / Text Capture:** The interface tracks only the binary presence of input, never capturing strings or semantic activity.
*   🚫 **Environmental Network Mapping:** Local Wi-Fi SSID details and geographic GPS telemetry are stripped by the network firewall before reaching the HR database.

---

## 2. Payroll Reconciliation Ledger Layout

The interface for payroll processing teams displays session persistence counts isolated from clinical context or case logs, ensuring complete diagnostic blindness.

| Column Identifier | Data Type | Constraint Rule | Purpose |
| :--- | :--- | :--- | :--- |
| `Anonymized_User_Hash` | Text (SHA-256) | Read-Only | Shields the individual's direct medical name from standard billing teams. |
| `Logged_Session_Hours` | Numeric (00.00) | Immutable | Records actual verified session persistence under Gate 2 authentication logs. |
| `Assigned_Labor_Code` | Text String | Hardcoded | Standardized exclusively to: `Approved Employment Preservation Accommodation Time`. |
| `Overtime_Exempt_Flag` | Boolean | System Auto-Set | Maps parameters to guarantee FLSA compliance bounds automatically. |

---

```text
This is for informational purposes only. For medical advice or diagnosis, consult a professional. AI responses may include mistakes.
```
