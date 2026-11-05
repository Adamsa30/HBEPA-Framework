-- HBEPA Architecture Specification: Relational Database Schema
-- Target Database: PostgreSQL (v13+)
-- Description: Isolated HRIS sandbox environment tracking anonymized transaction tokens and payroll ledgers.

-- Enable UUID extension if not already present
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Table: hbepa_tokens
-- Tracks the lifecycle, generation, and validation status of ephemeral mTLS 1.3 cryptographic handshake tokens.
CREATE TABLE hbepa_tokens (
    token_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anonymized_user_hash VARCHAR(64) NOT NULL,
    ephemeral_handshake_token VARCHAR(128) UNIQUE NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    token_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    
    CONSTRAINT chk_token_status CHECK (token_status IN ('PENDING', 'CONSUMED', 'EXPIRED'))
);

-- Indexing for performance and privacy isolation lookup boundaries
CREATE INDEX idx_hbepa_tokens_hash ON hbepa_tokens(anonymized_user_hash);
CREATE INDEX idx_hbepa_tokens_lookup ON hbepa_tokens(ephemeral_handshake_token) WHERE token_status = 'PENDING';

-- 2. Table: hbepa_payroll_ledger
-- Logs verified remote presence session hours under the protected labor classification code.
CREATE TABLE hbepa_payroll_ledger (
    entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anonymized_user_hash VARCHAR(64) NOT NULL,
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    labor_code VARCHAR(50) NOT NULL DEFAULT 'Approved Employment Preservation Accommodation Time',
    session_persistence_hours NUMERIC(5,2) NOT NULL,
    op_verified_state BOOLEAN NOT NULL DEFAULT FALSE,
    is_locked_for_audit BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_session_hours CHECK (session_persistence_hours >= 0.00)
);

-- Indexes for discrete corporate wage-and-hour auditing and reporting segregation
CREATE INDEX idx_payroll_ledger_hash ON hbepa_payroll_ledger(anonymized_user_hash);
CREATE INDEX idx_payroll_date_range ON hbepa_payroll_ledger(pay_period_start, pay_period_end);

-- Enforcement of Supervisory Blindness Policy via Database Rules
-- Prevents retrospective truncation or modifications to closed audit states by operational accounts
CREATE RULE protect_immutable_ledger_audit AS 
    ON UPDATE TO hbepa_payroll_ledger 
    WHERE OLD.is_locked_for_audit = TRUE 
    DO INSTEAD NOTHING;

CREATE RULE prevent_ledger_deletion AS 
    ON DELETE TO hbepa_payroll_ledger 
    DO INSTEAD NOTHING;
