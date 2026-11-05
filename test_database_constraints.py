# HBEPA Architecture Specification: Database Constraint Validation Tests
# Framework: pytest
# Target: PostgreSQL Sandbox Rules Enforcement Audit

import pytest
import psycopg2
import uuid
import datetime
from psycopg2.extras import RealDictCursor

# Database connection parameters configuration
DB_PARAMS = {
    "dbname": "hbepa_sandbox",
    "user": "hbepa_audit_user",
    "password": "SecureSandboxPassword123!",
    "host": "localhost",
    "port": 5432
}

@pytest.fixture(scope="module")
def db_connection():
    """Initializes and tears down an isolated testing database session connection."""
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = True
    yield conn
    conn.close()

@pytest.fixture
def cursor(db_connection):
    """Provides a transactional testing cursor with dictionary mapping capability."""
    cursor = db_connection.cursor(cursor_factory=RealDictCursor)
    yield cursor
    cursor.close()

def test_verify_privacy_by_design_hash_insertion(cursor):
    """Confirms that tracking metrics are written using an anonymized user hash index."""
    test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    test_token = "hbepa_tok_val_test_93810283918239102839123"
    expiration_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=14)
    
    # 1. Insert a mock anonymized handshake token block
    cursor.execute(
        \"\"\"
        INSERT INTO hbepa_tokens (anonymized_user_hash, ephemeral_handshake_token, expires_at, token_status)
        VALUES (%s, %s, %s, 'PENDING')
        RETURNING token_id;
        \"\"\",
        (test_hash, test_token, expiration_date)
    )
    token_record = cursor.fetchone()
    assert token_record is not None
    assert isinstance(token_record['token_id'], uuid.UUID)

def test_enforce_labor_code_isolation_default(cursor):
    """Validates that payroll ledgers automatically enforce the protected labor code string."""
    test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=14)
    
    # 2. Insert attendance entry omitting the labor code parameter to check table default string
    cursor.execute(
        \"\"\"
        INSERT INTO hbepa_payroll_ledger (anonymized_user_hash, pay_period_start, pay_period_end, session_persistence_hours)
        VALUES (%s, %s, %s, 40.00)
        RETURNING entry_id, labor_code;
        \"\"\",
        (test_hash, start_date, end_date)
    )
    ledger_record = cursor.fetchone()
    assert ledger_record['labor_code'] == 'Approved Employment Preservation Accommodation Time'

def test_verify_negative_session_hours_check_constraint(cursor):
    """Verifies that check constraints drop modifications with invalid negative tracking values."""
    test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=14)
    
    # 3. Force catch an exception when violating the numerical range rule
    with pytest.raises(psycopg2.errors.CheckViolation):
        cursor.execute(
            \"\"\"
            INSERT INTO hbepa_payroll_ledger (anonymized_user_hash, pay_period_start, pay_period_end, session_persistence_hours)
            VALUES (%s, %s, %s, -8.50);
            \"\"\",
            (test_hash, start_date, end_date)
        )

def test_audit_immutability_rules_prevent_retrospective_tampering(cursor):
    """Tests the PostgreSQL rule intercept to ensure closed locked-for-audit rows cannot be edited."""
    test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=14)
    
    # 4. Insert an active, baseline row that defaults to auto-locked for audit
    cursor.execute(
        \"\"\"
        INSERT INTO hbepa_payroll_ledger (anonymized_user_hash, pay_period_start, pay_period_end, session_persistence_hours, is_locked_for_audit)
        VALUES (%s, %s, %s, 35.50, TRUE)
        RETURNING entry_id;
        \"\"\",
        (test_hash, start_date, end_date)
    )
    entry_id = cursor.fetchone()['entry_id']
    
    # 5. Attempt a retrospective modification to update tracking hours
    cursor.execute(
        \"\"\"
        UPDATE hbepa_payroll_ledger 
        SET session_persistence_hours = 50.00 
        WHERE entry_id = %s;
        \"\"\",
        (entry_id,)
    )
    
    # 6. Query the row to verify the intercept trigger dropped the update command entirely
    cursor.execute("SELECT session_persistence_hours FROM hbepa_payroll_ledger WHERE entry_id = %s;", (entry_id,))
    assert cursor.fetchone()['session_persistence_hours'] == datetime.datetime.Decimal('35.50')

def test_audit_immutability_rules_prevent_deletion(cursor):
    """Confirms database rules intercept and block deletion requests on the attendance ledger table."""
    test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    start_date = datetime.date.today()
    
    cursor.execute(
        \"\"\"
        INSERT INTO hbepa_payroll_ledger (anonymized_user_hash, pay_period_start, pay_period_end, session_persistence_hours)
        VALUES (%s, %s, %s, 8.00)
        RETURNING entry_id;
        \"\"\",
        (test_hash, start_date, start_date)
    )
    entry_id = cursor.fetchone()['entry_id']
    
    # 7. Attempt an administrative delete request
    cursor.execute("DELETE FROM hbepa_payroll_ledger WHERE entry_id = %s;", (entry_id,))
    
    # 8. Check that the row was preserved seamlessly by the protection macro rule
    cursor.execute("SELECT COUNT(*) FROM hbepa_payroll_ledger WHERE entry_id = %s;", (entry_id,))
    assert cursor.fetchone()['count'] == 1
