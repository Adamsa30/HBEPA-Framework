# HBEPA Architecture Specification: Storage Maintenance & Performance Optimization
# Target Run Environment: Scheduled Server Task (Hourly/Daily System Cron)
# Purpose: Cleanse aged historical validation records to maximize index parsing.

import sys
import psycopg2
from database_retry_handler import execute_transaction_with_retry

# Relational connection sandbox parameters
DB_PARAMS = {
    "dbname": "hbepa_sandbox",
    "user": "hbepa_cron_daemon",
    "password": "SecureDaemonPassword789!",
    "host": "localhost",
    "port": 5432
}

def operational_cleanup_callback(cursor, historical_retention_days=90):
    """Transactional database logic sweeping expired tokens older than fixed thresholds."""
    print(f"[CLEANUP ENGINE] Scanning indexing trees for expired records older than {historical_retention_days} days...")
    
    # 1. Purge tokens that have reached hard lifecycle expiration holds
    cursor.execute(
        """
        DELETE FROM hbepa_tokens 
        WHERE token_status IN ('EXPIRED', 'CONSUMED') 
        AND expires_at < CURRENT_TIMESTAMP - INTERVAL '%s day'
        RETURNING token_id;
        """,
        (historical_retention_days,)
    )
    purged_records = cursor.fetchall()
    purged_count = len(purged_records)
    
    # 2. Log optimization metrics to system logs
    if purged_count > 0:
        print(f"[CLEANUP SUCCESS] Successfully purged {purged_count} decayed token structures from active indexes.")
    else:
        print("[CLEANUP ENGINE] Zero decayed validation tokens matched retention parameters. Storage layout remains optimal.")
        
    # 3. Re-index table targets to maintain maximum scannable efficiency
    print("[CLEANUP ENGINE] Executing transactional index optimization on table 'hbepa_tokens'...")
    cursor.execute("REINDEX TABLE hbepa_tokens;")
    return purged_count

def run_maintenance_sweep():
    """Triggers the transactional maintenance callback wrapper logic."""
    print("========================================================================")
    print("      HBEPA ENGINE MAINTENANCE: RELATIONAL STORAGE MAINTENANCE WINDOW")
    print("========================================================================")
    try:
        execute_transaction_with_retry(DB_PARAMS, operational_cleanup_callback, historical_retention_days=90)
        print("[SYSTEM SUMMARY] Storage optimization script completed successfully.")
    except Exception as error:
        print(f"[FATAL FAILURE] Maintenance optimization pass aborted: {str(error)}")
        sys.exit(1)

if __name__ == "__main__":
    run_maintenance_sweep()
