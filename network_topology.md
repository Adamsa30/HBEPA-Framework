       [ EXTERNAL CLINICAL NETWORK CORE ]
                       │
                       │ (Outgoing JSON Egress Block)
                       ▼
       ==================================================
       [ ENTERPRISE EXTERNAL PERIMETER EDGE FIREWALL ]
       ==================================================
                       │
                       │ Inbound Route: Port 443 / TCP
                       │ Enforced Constraint: Mutual TLS 1.3 Only
                       │ Cipher: TLS_AES_256_GCM_SHA384
                       ▼
 ┌────────────────────────────────────────────────────────────┐
 │  [ ISOLATED DMZ INGRESS CONTAINER ZONE ]                   │
 │                                                            │
 │  ┌──────────────────────────────────────────────────────┐  │
 │  │  api-gateway-proxy:8080                              │  │
 │  │  (Runtime Node: mock_clinical_callback_server.py)    │  │
 │  └──────────────────────────┬───────────────────────────┘  │
 └─────────────────────────────┼──────────────────────────────┘
                               │
                               │ [DEEP PACKET INSPECTION (DPI) FILTER]
                               │ Rule 1: Scan for "clinical_diagnosis", "symptoms"
                               │ Action: Programmatic String Key Strip & Drop
                               │ Rule 2: Convert to Flat Binary Verification Map
                               ▼
       ==================================================
       [ INTERNAL SECURITY ZONE BOUNDARY DATA FIREWALL ]
       ==================================================
                               │
                               │ Outbound Route: Port 5432 / TCP
                               │ Target Payload: {"anonymized_user_hash": "...", "op_verified": 1}
                               ▼
 ┌────────────────────────────────────────────────────────────┐
 │  [ TRUSTED SECURE INTERNAL CORE SUITE ]                    │
 │                                                            │
 │  ┌──────────────────────────────────────────────────────┐  │
 │  │  hbe-payroll-db:5432                                 │  │
 │  │  (PostgreSQL Instance: database_schema.sql)          │  │
 │  │  └─► Table: hbepa_tokens                             │  │
 │  │  └─► Table: hbepa_payroll_ledger                      │  │
 │  └──────────────────────────────────────────────────────┘  │
 └────────────────────────────────────────────────────────────┘
