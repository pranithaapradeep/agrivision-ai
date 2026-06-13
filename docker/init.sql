-- AgriVision AI — PostgreSQL Initialization
-- Runs once when the db container is first created.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for fast text search

-- Create application user (if not using the default)
-- CREATE USER agrivision WITH PASSWORD 'agrivision_pass';
-- GRANT ALL PRIVILEGES ON DATABASE agrivision_db TO agrivision;

-- Seed: default admin user (password: Admin@1234 bcrypt hashed)
-- The actual tables are created by SQLAlchemy on app startup (init_db).
-- This file pre-creates the DB and extensions only.

-- Create indexes hint table (actual indexes added by Alembic migrations)
COMMENT ON DATABASE agrivision_db IS 'AgriVision AI — Precision Agriculture Platform | SIH 2024';
