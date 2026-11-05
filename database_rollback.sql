  ┌────────────────────────────────────────────────────────────────────────┐
  │ 🌐 PRESENTATION LAYER (Dashboard Portal Specifications)                │
  │  └─► user_portal_spec.md       (Status Machine state filters)          │
  │  └─► portal_notifications.md   (Decoupled warning banner configurations)│
  └───────────────────────────────────┬────────────────────────────────────┘
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 🛡️ DATA FIREWALL LAYER (mTLS Proxies & Core Gateway Pipelines)          │
  │  └─► api_specification.md      (mTLS 1.3 JSON formatting rules)        │
  │  └─► mock_clinical_server.py   (Deep Packet Inspection string drops)   │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ ⚙️ CORE AUTOMATION ENGINE (Background Process Service Daemons)          │
  │  └─► validation_gate.py        (Tunnel persistence evaluation hooks)   │
  │  └─► disconnect_handler.py     (Microsecond session crash logging)     │
  │  └─► recertification_daemon.py (14-day administrative grace sweeps)     │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 🗃️ IMMUTABLE STORAGE LAYER (Relational Database Core Sandbox)          │
  │  └─► database_schema.sql       (PostgreSQL isolation rules & indexes)  │
  │  └─► retry_handler.py          (Exponential backoff with jitter macros)│
  │  └─► cleanup_cron.py           (Decayed validation key purging daemons)│
  └────────────────────────────────────────────────────────────────────────┘
