# HBEPA Secure Portal Interface: Automated Notification Templates

This directory houses the standard system templates dispatched to the employee's private dashboard by background cron daemons during Gate 4 lifecycle transitions.

---

## Template 1: INITIATE_ADMINISTRATIVE_GRACE_PERIOD
*   **System Trigger Event:** Expiration window <= 14 days; background mTLS 1.3 clinical token verification resolves as `PENDING` or `FAILED`.
*   **UI Banner Style:** Soft Amber Informational Alert (Strictly bars administrative panic or supervisor warning alerts).

### [SYSTEM NOTICE: Accommodation Block Status Update]
> **Status:** Active under 14-Day Administrative Grace Window  
> **Effective Date:** Generated Automatically on System Audit Lifecycle  
> **Assigned Labor Code:** `Approved Employment Preservation Accommodation Time`

Dear Participant,

This automated notice confirms that your current 90-day Home-Based Employment Preservation Accommodation block is approaching its standard lifecycle review interval. 

Because our background system sync with your regional healthcare network's isolated validation module has not yet received a refreshed binary indicator string, the system has **automatically activated your protected 14-Day Administrative Grace Window**. 

**What this means for your daily schedule:**
1. **Employment Continuity is Locked:** Your remote network access sessions remain fully authorized. Your daily clock-in and clock-out routines are entirely unaffected.
2. **Payroll Integration is Maintained:** Every verified hour of session persistence will continue to log seamlessly under your standard accommodation labor code.
3. **Total Privacy Enforced:** Your supervisor and line managers have **zero visibility** into this notification. Your block cannot be manually altered or paused by operational staff.

Please log into your secure health portal link or reach out to your designated *Occupational Health Liaison* within the next 14 days to request that your primary care office (e.g., IU Health Primary Care) refreshes your functional barrier verification string (`{"op_verified": 1}`).

---

## Template 2: AUTO_EXTEND_ACCOMMODATION_BLOCK
*   **System Trigger Event:** Expiration window <= 14 days; background mTLS 1.3 clinical token resolves successfully as `CONSUMED` (`{"op_verified": 1}`).
*   **UI Banner Style:** Soft Green Confirmation Badge.

### [SYSTEM NOTICE: Lifecycle Extension Confirmed]
> **Status:** Auto-Extended (Consecutive 90-Day Block)  
> **Designation:** Immutable Workforce Preservation Protection

Dear Participant,

Our background *Status Sync开 Daemon* has successfully processed a refreshed verification token via a secure mTLS connection. Your structural remote presence accommodation has been **automatically extended for a matching consecutive 90-day block**.

No manual action is required on your part. Your line managers have been notified only that your remote presence connection window remains authorized. Thank you for your continued participation in the reference pilot program.

---

```text
This is for informational purposes only. For medical advice or diagnosis, consult a professional. AI responses may include mistakes.
```
