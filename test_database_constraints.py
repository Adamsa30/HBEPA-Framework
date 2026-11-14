import pytest
import psycopg2
import uuid
import datetime
from decimal import Decimal
from psycopg2.extras import RealDictCursor

DB_PARAMS = {
    "dbname": "hbepa_sandbox",
    "user": "hbepa_audit_user",
    "password": "SecureSandboxPassword123!",
    "host": "localhost",
    "port": 5432
}

@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = True
    yield conn
    conn.close()

@pytest.fixture
def cursor(db_connection):
    cursor = db_connection.cursor(cursor_factory=RealDictCursor)
    yield cursor
    cursor.close()

def test_verify_privacy_by_design_hash_insertion(cursor):
    test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    test_token = "hbepa_tok_val_test_93810283918239102839123"
    expiration_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)

    cursor.execute(
        "INSERT INTO hbepa_tokens (anonymized_user_hash, ephemeral_handshake_token, expires_at, token_status) VALUES (%s, %s, %s, 'PENDING') RETURNING token_id;",
        (test_hash, test_token, expiration_date)
    )
    token_record = cursor.fetchone()
    assert token_record is not None
    assert isinstance(token_record['token_id'], uuid.UUID)

def test_enforce_labor_code_isolation_default(cursor):
    test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=14)

    cursor.execute(
        "INSERT INTO hbepa_payroll_ledger (anonymized_user_hash, pay_period_start, pay_period_end, session_persistence_hours) VALUES (%s, %s, %s, 40.00) RETURNING entry_id, labor_code;",
        (test_hash, start_date, end_date)
    )
    ledger_record = cursor.fetchone()
    assert ledger_record['labor_code'] == 'Approved Employment Preservation Accommodation Time'

def test_verify_negative_session_hours_check_constraint(cursor):
    test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=14)

    with pytest.raises(psycopg2.errors.CheckViolation):
        cursor.execute(
            "INSERT INTO hbepa_payroll_ledger (anonymized_user_hash, pay_period_start, pay_period_end, session_persistence_hours) VALUES (%s, %s, %s, -8.50);",
            (test_hash, start_date, end_date)
        )

def test_audit_immutability_rules_prevent_retrospective_tampering(cursor):
    test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=14)

    cursor.execute(
        "INSERT INTO hbepa_payroll_ledger (anonymized_user_hash, pay_period_start, pay_period_end, session_persistence_hours, is_locked_for_audit) VALUES (%s, %s, %s, 35.50, TRUE) RETURNING entry_id;",
        (test_hash, start_date, end_date)
    )
    entry_id = cursor.fetchone()['entry_id']

    cursor.execute(
        "UPDATE hbepa_payroll_ledger SET session_persistence_hours = 50.00 WHERE entry_id = %s;",
        (entry_id,)
    )

    cursor.execute("SELECT session_persistence_hours FROM hbepa_payroll_ledger WHERE entry_id = %s;", (entry_id,))
    assert cursor.fetchone()['session_persistence_hours'] == Decimal('35.50')

def test_audit_immutability_rules_prevent_deletion(cursor):
    test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    start_date = datetime.date.today()

    cursor.execute(
        "INSERT INTO hbepa_payroll_ledger (anonymized_user_hash, pay_period_start, pay_period_end, session_persistence_hours) VALUES (%s, %s, %s, 8.00) RETURNING entry_id;",
        (test_hash, start_date, start_date)
    )
    entry_id = cursor.fetchone()['entry_id']

    cursor.execute("DELETE FROM hbepa_payroll_ledger WHERE entry_id = %s;", (entry_id,))

    cursor.execute("SELECT COUNT(*) FROM hbepa_payroll_ledger WHERE entry_id = %s;", (entry_id,))
    assert cursor.fetchone()['count'] == 1
