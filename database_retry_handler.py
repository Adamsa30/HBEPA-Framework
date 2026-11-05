# HBEPA Architecture Specification: Relational Storage Connection Retry Engine
# Target Run Environment: Core Core Daemon Wrap / System Integration Component
# Purpose: Implements exponential backoff with jitter to protect transaction writes.

import time
import random
import psycopg2
import sys

# Target baseline database parameter specifications
MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 2.0
MAX_BACKOFF_SECONDS = 30.0

def execute_transaction_with_retry(db_config, database_operation_callback, *args, **kwargs):
    """Executes a database callback function within a highly resilient retry loop."""
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            # Attempt connection to the private PostgreSQL cluster zone
            connection = psycopg2.connect(**db_config)
            connection.autocommit = False  # Enforce transaction isolation boundaries
            
            try:
                with connection.cursor() as cursor:
                    # Invoke the passed operation macro logic
                    result = database_operation_callback(cursor, *args, **kwargs)
                    connection.commit()
                    print(f"[RETRY ENGINE] Transaction executed and committed successfully on attempt {retries + 1}.")
                    return result
            except Exception as transaction_error:
                connection.rollback()
                print(f"[RETRY ENGINE] Internal transaction error encountered: {str(transaction_error)}. Rolling back updates.")
                raise transaction_error
            finally:
                connection.close()
                
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as connection_fault:
            retries += 1
            if retries >= MAX_RETRIES:
                print(f"[FATAL FAULT] Exhausted maximum retry limit ({MAX_RETRIES}). Resiliency engine halting.")
                raise connection_fault
            
            # Calculate exponential backoff interval boundary with random jitter additions
            backoff_delay = min(MAX_BACKOFF_SECONDS, BASE_BACKOFF_SECONDS * (2 ** retries))
            jitter_modifier = random.uniform(0, 1.0) * backoff_delay
            final_sleep_duration = backoff_delay + jitter_modifier
            
            print(f"[RETRY ENGAGED] Database connectivity fault down link: {str(connection_fault)}")
            print(f"[RETRY ENGAGED] Retrying operation in {final_sleep_duration:.2f} seconds (Attempt {retries}/{MAX_RETRIES})...")
            time.sleep(final_sleep_duration)

# Mock operational task callback to simulate live ledger seeding 
def mock_write_ledger_entry(cursor, anonymized_hash, hours_value):
    """Appends an anonymous session log into the structural database schema."""
    cursor.execute(
        """
        INSERT INTO hbepa_payroll_ledger (anonymized_user_hash, pay_period_start, pay_period_end, session_persistence_hours)
        VALUES (%s, CURRENT_DATE, CURRENT_DATE + 14, %s)
        RETURNING entry_id;
        """,
        (anonymized_hash, hours_value)
    )
    return cursor.fetchone()[0]

if __name__ == "__main__":
    print("[SYSTEM CHECK] Database Retry Handler wrapper module compiled successfully.")
    sys.exit(0)
