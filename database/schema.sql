-- ==============================================================================
-- Little Steps Tracker - Growth Monitoring Module Database Schema
-- Module: Person 3 (Growth Monitoring Backend & Database)
-- Target Database: PostgreSQL (Default port: 5432)
-- Database Name: little_steps_tracker
-- ==============================================================================

-- Optional: Create database if it does not already exist
-- (Run this command as PostgreSQL superuser/admin)
-- CREATE DATABASE little_steps_tracker;

-- Connect to the database:
-- \c little_steps_tracker;

-- Create growth_records table
CREATE TABLE IF NOT EXISTS growth_records (
    id SERIAL PRIMARY KEY,
    child_id VARCHAR(50) NOT NULL,
    measurement_date DATE NOT NULL,
    height NUMERIC(5, 2) NOT NULL CHECK (height > 0),
    weight NUMERIC(5, 2) NOT NULL CHECK (weight > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Index for efficient child lookup and history ordering by measurement date
CREATE INDEX IF NOT EXISTS idx_growth_records_child_date 
    ON growth_records (child_id, measurement_date DESC);

-- Column and Table Comments for documentation clarity
COMMENT ON TABLE growth_records IS 'Stores raw child growth measurement records (height and weight). Handled by Person 3.';
COMMENT ON COLUMN growth_records.id IS 'Auto-incrementing unique identifier for each measurement record';
COMMENT ON COLUMN growth_records.child_id IS 'Unique child identifier reference from Child Management (Person 1), e.g. LST-001';
COMMENT ON COLUMN growth_records.measurement_date IS 'Date when the physical measurement was recorded';
COMMENT ON COLUMN growth_records.height IS 'Child height in centimeters (cm). Must be strictly positive (> 0)';
COMMENT ON COLUMN growth_records.weight IS 'Child weight in kilograms (kg). Must be strictly positive (> 0)';
COMMENT ON COLUMN growth_records.created_at IS 'Server timestamp when the record was inserted into the database';
