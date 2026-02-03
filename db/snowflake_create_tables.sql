-- CheckMoYan: Create tables in Snowflake
-- Run this in a Snowflake SQL worksheet. Creates database/schema first, then tables.
-- (Use the same database/schema names in .streamlit/secrets.toml [SNOWFLAKE].)

CREATE DATABASE IF NOT EXISTS CHECKMOYAN;
CREATE SCHEMA IF NOT EXISTS CHECKMOYAN.PUBLIC;

USE DATABASE CHECKMOYAN;
USE SCHEMA PUBLIC;

-- ========== USERS ==========
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    plan VARCHAR(50) NOT NULL DEFAULT 'free',
    premium_until DATE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ========== USAGE (daily check counts) ==========
CREATE TABLE IF NOT EXISTS usage (
    email VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    checks_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (email, date)
);

-- ========== SCANS ==========
CREATE SEQUENCE IF NOT EXISTS scans_seq START 1 INCREMENT 1;

CREATE TABLE IF NOT EXISTS scans (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT scans_seq.NEXTVAL,
    email VARCHAR(255) NOT NULL,
    ts TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    verdict VARCHAR(50) NOT NULL,
    confidence INTEGER NOT NULL,
    category VARCHAR(255),
    signals_json VARCHAR(65535),
    msg_hash VARCHAR(255)
);

-- ========== UPGRADE_REQUESTS ==========
CREATE SEQUENCE IF NOT EXISTS upgrade_requests_seq START 1 INCREMENT 1;

CREATE TABLE IF NOT EXISTS upgrade_requests (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT upgrade_requests_seq.NEXTVAL,
    email VARCHAR(255) NOT NULL,
    plan VARCHAR(50) NOT NULL,
    method VARCHAR(50),
    ref VARCHAR(255),
    receipt_path VARCHAR(1024),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    ts TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    admin_notes VARCHAR(65535),
    approved_until DATE
);

-- ========== COMMUNITY_ALERTS ==========
CREATE SEQUENCE IF NOT EXISTS community_alerts_seq START 1 INCREMENT 1;

CREATE TABLE IF NOT EXISTS community_alerts (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT community_alerts_seq.NEXTVAL,
    category VARCHAR(255) NOT NULL,
    summary VARCHAR(65535),
    ts TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ========== APP_SETTINGS (payment config from Admin) ==========
CREATE TABLE IF NOT EXISTS app_settings (
    key VARCHAR(255) PRIMARY KEY,
    value VARCHAR(65535) NOT NULL DEFAULT ''
);
