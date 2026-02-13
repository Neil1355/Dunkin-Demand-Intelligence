-- Add QR codes table for storing store-specific QR codes
-- One QR code per store, no regeneration if already exists

CREATE TABLE IF NOT EXISTS qr_codes (
  id SERIAL PRIMARY KEY,
  store_id INTEGER NOT NULL UNIQUE,
  qr_data TEXT NOT NULL,  -- Base64 encoded PNG data
  qr_url TEXT NOT NULL,   -- Target URL that QR code points to
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- Foreign key to stores table (if needed, otherwise just store_id as reference)
  -- FOREIGN KEY (store_id) REFERENCES stores(id)
  
  CONSTRAINT qr_codes_store_unique UNIQUE (store_id)
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_qr_codes_store_id ON qr_codes(store_id);
CREATE INDEX IF NOT EXISTS idx_qr_codes_created_at ON qr_codes(created_at);

-- Audit log for QR code access
CREATE TABLE IF NOT EXISTS qr_access_log (
  id SERIAL PRIMARY KEY,
  qr_code_id INTEGER NOT NULL,
  store_id INTEGER NOT NULL,
  accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ip_address VARCHAR(45),
  user_agent TEXT,
  action VARCHAR(50),  -- 'scan', 'download', 'view'
  
  FOREIGN KEY (qr_code_id) REFERENCES qr_codes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_qr_access_log_store_id ON qr_access_log(store_id);
CREATE INDEX IF NOT EXISTS idx_qr_access_log_accessed_at ON qr_access_log(accessed_at);
