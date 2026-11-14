# HBEPA Database Integrity, Privacy & Audit Enforcement Tests
# Framework: pytest
# Target: PostgreSQL Sandbox Rules Enforcement Audit

import os
import uuid
import hashlib
import datetime
from decimal import Decimal

import pytest
import psycopg2
from psycopg2.extras import RealDictCursor


DB_PARAMS = {
    "dbname": os.getenv("HBEPA_DB_NAME", "hbepa_sandbox"),
    "user": os.getenv("HBEPA_DB_USER", "hbepa_audit_user"),
    "password": os.getenv("HBEPA_DB_PASSWORD", "SecureSandboxPassword123!"),
    "host": os.getenv("HBEPA_DB_HOST", "localhost"),
    "port": int(os.getenv("HBEPA_DB_PORT", "5432")),
    "connect_timeout": 10,
}

EXPECTED_LABOR_CODE_PREFIX = "Approved Employment Preservation Accommodation"


@pytest.fixture(scope="function")
def db_connection():
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = False
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


@pytest.fixture(scope="function")
def cursor(db_connection):
    db_cursor = db_connection.cursor(cursor_factory=RealDictCursor)
    try:
        yield db_cursor
    finally:
        db_cursor.close()


def generate_anonymized_user_hash():
    unique_value = str(uuid.uuid4()).encode("utf-8")
    return hashlib.sha256(unique_value).hexdigest()


def generate_pay_period():
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=14)
    return start_date, end_date


def insert_payroll_record(cursor, hours=Decimal("35.50"), locked=True):
    user_hash = generate_anonymized_user_hash()
    start_date, end_date = generate_pay_period()
    cursor.execute(
        "INSERT INTO hbepa_payroll_ledger (anonymized_user_hash, pay_period_start, pay_period_end, session_persistence_hours, is_locked_for_audit) VALUES (%s, %s, %s, %s, %s) RETURNING entry_id, labor_code, session_persistence_hours;",
        (user_hash, start_date, end_date, hours, locked),
    )
    return cursor.fetchone()


def test_verify_privacy_by_design_hash_insertion(cursor):
    test_hash = generate_anonymized_user_hash()
    test_token = f"hbepa_test_{uuid.uuid4().hex}"
    expiration_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)

    cursor.execute(
        "INSERT INTO hbepa_tokens (anonymized_user_hash, ephemeral_handshake_token, expires_at, token_status) VALUES (%s, %s, %s, 'PENDING') RETURNING token_id, anonymized_user_hash, ephemeral_handshake_token, expires_at;",
        (test_hash, test_token, expiration_date),
    )
    token_record = cursor.fetchone()

    assert token_record is not None
    assert isinstance(token_record["token_id"], uuid.UUID)
    assert token_record["anonymized_user_hash"] == test_hash
    assert token_record["ephemeral_handshake_token"] == test_token
    assert token_record["expires_at"] is not None


def test_enforce_labor_code_isolation_default(cursor):
    ledger_record = insert_payroll_record(cursor, hours=Decimal("40.00"), locked=False)

    assert ledger_record is not None
    assert ledger_record["entry_id"] is not None
    labor_code = ledger_record["labor_code"]
    assert isinstance(labor_code, str)
    assert labor_code.startswith(EXPECTED_LABOR_CODE_PREFIX)


def test_verify_negative_session_hours_check_constraint(cursor):
    test_hash = generate_anonymized_user_hash()
    start_date, end_date = generate_pay_period()

    with pytest.raises(psycopg2.errors.CheckViolation):
        cursor.execute(
            "INSERT INTO hbepa_payroll_ledger (anonymized_user_hash, pay_period_start, pay_period_end, session_persistence_hours) VALUES (%s, %s, %s, %s);",
            (test_hash, start_date, end_date, Decimal("-8.50")),
        )


def test_audit_immutability_rules_prevent_retrospective_tampering(cursor):
    ledger_record = insert_payroll_record(cursor, hours=Decimal("35.50"), locked=True)
    entry_id = ledger_record["entry_id"]
    original_hours = ledger_record["session_persistence_hours"]

    cursor.execute("SAVEPOINT immutability_update")
    try:
        cursor.execute(
            "UPDATE hbepa_payroll_ledger SET session_persistence_hours = %s WHERE entry_id = %s;",
            (Decimal("50.00"), entry_id),
        )
        cursor.execute("RELEASE SAVEPOINT immutability_update")
    except psycopg2.Error:
        cursor.execute("ROLLBACK TO SAVEPOINT immutability_update")
        cursor.execute("RELEASE SAVEPOINT immutability_update")

    cursor.execute(
        "SELECT session_persistence_hours FROM hbepa_payroll_ledger WHERE entry_id = %s;",
        (entry_id,),
    )
    updated_record = cursor.fetchone()
    assert updated_record is not None
    assert updated_record["session_persistence_hours"] == original_hours


def test_audit_immutability_rules_prevent_deletion(cursor):
    ledger_record = insert_payroll_record(cursor, hours=Decimal("8.00"), locked=True)
    entry_id = ledger_record["entry_id"]

    cursor.execute("SAVEPOINT immutability_delete")
    try:
        cursor.execute(
            "DELETE FROM hbepa_payroll_ledger WHERE entry_id = %s;",
            (entry_id,),
        )
        cursor.execute("RELEASE SAVEPOINT immutability_delete")
    except psycopg2.Error:
        cursor.execute("ROLLBACK TO SAVEPOINT immutability_delete")
        cursor.execute("RELEASE SAVEPOINT immutability_delete")

    cursor.execute(
        "SELECT COUNT(*) AS record_count FROM hbepa_payroll_ledger WHERE entry_id = %s;",
        (entry_id,),
    )
    result = cursor.fetchone()
    assert result["record_count"] == 1
