-- Migration: Add pending waste submissions table
-- Purpose: Allow employees to submit waste counts via QR code for manager approval

-- Create pending_waste_submissions table
CREATE TABLE IF NOT EXISTS pending_waste_submissions (
    id SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL,
    submitter_name VARCHAR(100) NOT NULL,
    donut_count INTEGER DEFAULT 0,
    munchkin_count INTEGER DEFAULT 0,
    other_count INTEGER DEFAULT 0,
    notes TEXT,
    submission_date DATE NOT NULL DEFAULT CURRENT_DATE,
    submitted_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, edited, discarded
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP,
    ip_address VARCHAR(45), -- IPv4 or IPv6
    user_agent TEXT
);

-- Create indexes for performance
CREATE INDEX idx_pending_waste_store_status ON pending_waste_submissions(store_id, status);
CREATE INDEX idx_pending_waste_date ON pending_waste_submissions(submission_date);
CREATE INDEX idx_pending_waste_submitted_at ON pending_waste_submissions(submitted_at DESC);

-- Add comments for documentation
COMMENT ON TABLE pending_waste_submissions IS 'Stores employee waste submissions pending manager approval';
COMMENT ON COLUMN pending_waste_submissions.status IS 'pending: awaiting review, approved: accepted as-is, edited: modified by manager, discarded: rejected';
COMMENT ON COLUMN pending_waste_submissions.reviewed_by IS 'User ID of manager who reviewed the submission';
