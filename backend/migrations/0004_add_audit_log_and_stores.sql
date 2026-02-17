-- Audit logging table for security and compliance
-- Tracks all significant user actions: login, data changes, exports, etc.

CREATE TABLE IF NOT EXISTS audit_log (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,  -- NULL for system actions
  action_type VARCHAR(50) NOT NULL,
  resource_type VARCHAR(50),
  resource_id INTEGER,
  ip_address VARCHAR(45),
  user_agent TEXT,
  details JSONB,
  status VARCHAR(20),  -- 'success', 'failure', 'warning'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action_type ON audit_log(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_resource ON audit_log(resource_type, resource_id);

-- Store table to track store locations
CREATE TABLE IF NOT EXISTS stores (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  location VARCHAR(255),
  address VARCHAR(255),
  city VARCHAR(100),
  state VARCHAR(2),
  zip_code VARCHAR(10),
  phone VARCHAR(20),
  manager_id INTEGER,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_stores_manager_id ON stores(manager_id);
CREATE INDEX IF NOT EXISTS idx_stores_is_active ON stores(is_active);
