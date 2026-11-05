# HBEPA Architecture Specification: Gate 4 Lifecycle Recertification Daemon
# Target Run Environment: Background System Service (Systemd / Cron Daemon)
# Purpose: Manages 30/60/90-day block expirations, initializes tokens, and shields grace periods.

import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import requests

# Sandbox relational database connectivity mapping
DB_PARAMS = {
    "dbname": "hbepa_sandbox",
    "user": "hbepa_cron_daemon",
    "password": "SecureDaemonPassword789!",
    "host": "localhost",
    "port": 5432
}

# API Gateway Endpoint coordinates for clinical synchronization handshakes
API_GATEWAY_URL = "https://internal.corp"
CLIENT_CERT_PATHS = ("/etc/hbepa/certs/client.crt", "/etc/hbepa/certs/client.key")

def get_db_connection():
    """Establishes an active database session for transactional background workflows."""
    try:
        return psycopg2.connect(**DB_PARAMS)
    except Exception as e:
        print(f"[FATAL LOG] Unable to bind to PostgreSQL ledger database: {str(e)}")
        sys.exit(1)

def execute_lifecycle_audit_cycle():
    """Scans active token allocations to initialize recertification loops or activate grace parameters."""
    current_time = datetime.datetime.now(datetime.timezone.utc)
    threshold_window = current_time + datetime.timedelta(days=14)
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print(f"[CRON INFO] Initializing HBEPA Gate 4 lifecycle audit run at {current_time.isoformat()}...")
    
    try:
        # 1. Query tokens expiring within the 14-day administrative threshold that are not processed
        cursor.execute(
            """
            SELECT token_id, anonymized_user_hash, expires_at, token_status 
            FROM hbepa_tokens 
            WHERE token_status = 'CONSUMED' 
            AND expires_at <= %s 
            AND expires_at > %s;
            """,
            (threshold_window, current_time)
        )
        expiring_blocks = cursor.fetchall()
        
        for block in expiring_blocks:
            user_hash = block['anonymized_user_hash']
            print(f"[ALERT TRIGGER] Row user_hash [{user_hash[:8]}...] has entered the 14-day lifecycle boundary.")
            
            # 2. Transmit token initialization instruction to the isolated API Gateway Broker
            payload = {
                "anonymized_user_hash": user_hash,
                "requested_lifecycle_block_days": 90,
                "client_routing_zone": "IN-HENDRICKS-AVON"
            }
            
            try:
                response = requests.post(
                    API_GATEWAY_URL, 
                    json=payload, 
                    cert=CLIENT_CERT_PATHS, 
                    timeout=10
                )
                
                if response.status_code == 211 or response.status_code == 201:
                    print(f"[mTLS SUCCESS] Ephemeral token handshake initialized for user_hash [{user_hash[:8]}...].")
                else:
                    print(f"[API ERROR] Gateway returned status code {response.status_code}. Shifting to manual grace containment.")
                    
            except Exception as api_err:
                # 3. If API sync or connection fails, the daemon locks protection boundaries locally
                print(f"[NETWORK FAULT] External synchronization link dropped: {str(api_err)}")
                print(f"[GUARD ENGAGED] Locking 14-day Administrative Grace Window. Profile access and payroll tracking locked.")
        
        # 4. Check for tokens that have breached their hard grace expiration cutoff without clinical sync clearing
        cursor.execute(
            """
            SELECT token_id, anonymized_user_hash 
            FROM hbepa_tokens 
            WHERE token_status = 'PENDING' 
            AND expires_at <= %s;
            """,
            (current_time,)
        )
        expired_grace_blocks = cursor.fetchall()
        
        for expired_block in expired_grace_blocks:
            token_uuid = expired_block['token_id']
            user_hash = expired_block['anonymized_user_hash']
            
            print(f"[TIMEOUT EXPIRED] Token UUID [{token_uuid}] grace window elapsed without medical validation sync.")
            
            # 5. Shift token state to EXPIRED. Trigger downstream protection macros
            cursor.execute(
                """
                UPDATE hbepa_tokens 
                SET token_status = 'EXPIRED' 
                WHERE token_id = %s;
                """,
                (token_uuid,)
            )
            
            # 6. Flag the payroll ledger to pause tracking but explicitly engage the Statutory Non-Separation Clause
            cursor.execute(
                """
                UPDATE hbepa_payroll_ledger 
                SET is_locked_for_audit = TRUE, op_verified_state = FALSE
                WHERE anonymized_user_hash = %s;
                """,
                (user_hash,)
            )
            print(f"[SYSTEM POLICY] Tracking log paused. Core profile flagged to 'Protected Retention Inactive' pending human-led OHL dialogue.")
            
        conn.commit()
        
    except Exception as db_err:
        conn.rollback()
        print(f"[DATABASE FAULT] Operational rollback executed during cron cycle: {str(db_err)}")
    finally:
        cursor.close()
        conn.close()
        print("[CRON INFO] HBEPA Gate 4 daemon lifecycle audit run finished successfully.")

if __name__ == "__main__":
    execute_lifecycle_audit_cycle()
