
"""
HBEPA Database Integrity, Privacy & Audit Enforcement Tests

Purpose:
    Validate database-level protections for the Home-Based Employment
    Preservation Accommodation (HBEPA) framework.

Coverage:
    1. Privacy-by-design token insertion.
    2. UUID-based token identification.
    3. Payroll labor-code isolation.
    4. Prevention of negative session hours.
    5. Protection against retrospective audit modification.
    6. Protection against unauthorized audit deletion.

Requirements:
    pytest
    psycopg2-binary
    PostgreSQL with the HBEPA schema initialized.
"""

import os
import uuid
import hashlib
import datetime
from decimal import Decimal

import pytest
import psycopg2
from psycopg2.extras import RealDictCursor


# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------

DB_PARAMS = {
    "dbname": os.getenv("HBEPA_DB_NAME", "hbepa_sandbox"),
    "user": os.getenv("HBEPA_DB_USER", "hbepa_audit_user"),
    "password": os.getenv("HBEPA_DB_PASSWORD", ""),
    "host": os.getenv("HBEPA_DB_HOST", "localhost"),
    "port": int(os.getenv("HBEPA_DB_PORT", "5432")),
    "connect_timeout": 10,
}


EXPECTED_LABOR_CODE_PREFIX = (
    "Approved Employment Preservation Accommodation"
)

EXPECTED_SESSION_HOURS = Decimal("35.50")


# ---------------------------------------------------------
# DATABASE FIXTURES
# ---------------------------------------------------------

@pytest.fixture(scope="function")
def db_connection():
    """Create an isolated database connection for each test."""

    connection = psycopg2.connect(**DB_PARAMS)
    connection.autocommit = False

    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()


@pytest.fixture(scope="function")
def cursor(db_connection):
    """Provide a dictionary-based cursor."""

    db_cursor = db_connection.cursor(
        cursor_factory=RealDictCursor
    )

    try:
        yield db_cursor
    finally:
        db_cursor.close()


# ---------------------------------------------------------
# TEST DATA GENERATION
# ---------------------------------------------------------

def generate_anonymized_user_hash():
    """Generate a SHA-256 identifier without exposing user identity."""

    unique_value = str(uuid.uuid4()).encode("utf-8")

    return hashlib.sha256(unique_value).hexdigest()


def generate_pay_period():
    """Generate a valid 14-day payroll period."""

    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=14)

    return start_date, end_date


def insert_payroll_record(cursor):
    """Create a payroll record using database-defined defaults."""

    user_hash = generate_anonymized_user_hash()
    start_date, end_date = generate_pay_period()

    cursor.execute(
        """
        INSERT INTO hbepa_payroll_ledger (
            anonymized_user_hash,
            pay_period_start,
            pay_period_end
        )
        VALUES (%s, %s, %s)
        RETURNING entry_id, labor_code,
                  session_persistence_hours;
        """,
        (user_hash, start_date, end_date),
    )

    return cursor.fetchone()


# ---------------------------------------------------------
# TEST 1: PRIVACY-BY-DESIGN TOKEN INSERTION
# ---------------------------------------------------------

def test_verify_privacy_by_design_hash_insertion(cursor):
    """Verify secure token insertion and UUID identification."""

    test_hash = generate_anonymized_user_hash()
    test_token = f"hbepa_test_{uuid.uuid4().hex}"

    expiration_date = (
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=24)
    )

    cursor.execute(
        """
        INSERT INTO hbepa_tokens (
            anonymized_user_hash,
            ephemeral_handshake_token,
            expires_at
        )
        VALUES (%s, %s, %s)
        RETURNING token_id, anonymized_user_hash,
                  ephemeral_handshake_token, expires_at;
        """,
        (test_hash, test_token, expiration_date),
    )

    token_record = cursor.fetchone()

    assert token_record is not None
    assert isinstance(token_record["token_id"], uuid.UUID)
    assert token_record["anonymized_user_hash"] == test_hash
    assert token_record["ephemeral_handshake_token"] == test_token
    assert token_record["expires_at"] is not None


# ---------------------------------------------------------
# TEST 2: LABOR-CODE ISOLATION
# ---------------------------------------------------------

def test_enforce_labor_code_isolation_default(cursor):
    """Verify that payroll records receive the approved HBEPA code."""

    ledger_record = insert_payroll_record(cursor)

    assert ledger_record is not None
    assert ledger_record["entry_id"] is not None

    labor_code = ledger_record["labor_code"]

    assert isinstance(labor_code, str)
    assert labor_code.startswith(EXPECTED_LABOR_CODE_PREFIX)


# ---------------------------------------------------------
# TEST 3: NEGATIVE SESSION HOURS CONSTRAINT
# ---------------------------------------------------------

def test_verify_negative_session_hours_check_constraint(cursor):
    """Ensure the database rejects negative employment hours."""

    test_hash = generate_anonymized_user_hash()
    start_date, end_date = generate_pay_period()

    with pytest.raises(psycopg2.errors.CheckViolation):

        cursor.execute(
            """
            INSERT INTO hbepa_payroll_ledger (
                anonymized_user_hash,
                pay_period_start,
                pay_period_end,
                session_persistence_hours
            )
            VALUES (%s, %s, %s, %s);
            """,
            (
                test_hash,
                start_date,
                end_date,
                Decimal("-1.00"),
            ),
        )


# ---------------------------------------------------------
# TEST 4: AUDIT RECORD IMMUTABILITY
# ---------------------------------------------------------

def test_audit_immutability_rules_prevent_retrospective_tampering(
    cursor,
    db_connection,
):
    """
    Verify that historical payroll hours cannot be altered.

    An update may be rejected by the database or ignored by an
    immutability trigger. In either case, the original value
    must remain unchanged.
    """

    ledger_record = insert_payroll_record(cursor)

    entry_id = ledger_record["entry_id"]
    original_hours = ledger_record["session_persistence_hours"]

    assert original_hours == EXPECTED_SESSION_HOURS

    cursor.execute("SAVEPOINT immutability_update")

    try:
        cursor.execute(
            """
            UPDATE hbepa_payroll_ledger
            SET session_persistence_hours = %s
            WHERE entry_id = %s;
            """,
            (Decimal("50.00"), entry_id),
        )

        cursor.execute("RELEASE SAVEPOINT immutability_update")

    except psycopg2.Error:
        cursor.execute(
            "ROLLBACK TO SAVEPOINT immutability_update"
        )
        cursor.execute("RELEASE SAVEPOINT immutability_update")

    cursor.execute(
        """
        SELECT session_persistence_hours
        FROM hbepa_payroll_ledger
        WHERE entry_id = %s;
        """,
        (entry_id,),
    )

    updated_record = cursor.fetchone()

    assert updated_record is not None
    assert updated_record["session_persistence_hours"] == original_hours


# ---------------------------------------------------------
# TEST 5: AUDIT RECORD DELETION PROTECTION
# ---------------------------------------------------------

def test_audit_immutability_rules_prevent_deletion(
    cursor,
):
    """
    Verify that historical payroll records cannot be deleted.

    The database must reject or prevent unauthorized deletion.
    """

    ledger_record = insert_payroll_record(cursor)

    entry_id = ledger_record["entry_id"]

    cursor.execute("SAVEPOINT immutability_delete")

    try:
        cursor.execute(
            """
            DELETE FROM hbepa_payroll_ledger
            WHERE entry_id = %s;
            """,
            (entry_id,),
        )

        cursor.execute("RELEASE SAVEPOINT immutability_delete")

    except psycopg2.Error:
        cursor.execute(
            "ROLLBACK TO SAVEPOINT immutability_delete"
        )
        cursor.execute("RELEASE SAVEPOINT immutability_delete")

    cursor.execute(
        """
        SELECT COUNT(*) AS record_count
        FROM hbepa_payroll_ledger
        WHERE entry_id = %s;
        """,
        (entry_id,),
    )

    result = cursor.fetchone()

    assert result["record_count"] == 1


# ---------------------------------------------------------
# END OF HBEPA DATABASE INTEGRITY TEST SUITE
# ---------------------------------------------------------
