-- Create table for call alerts with timezone support
CREATE TABLE IF NOT EXISTS call_alerts (
    xdrid VARCHAR(36) PRIMARY KEY,
    tenant VARCHAR(50),
    val_euro DECIMAL(10,2),
    duration INTEGER,
    raw_caller_number VARCHAR(20),
    raw_called_number VARCHAR(20),
    timestamp TIMESTAMPTZ,
    event_time TIMESTAMPTZ,
    processing_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    carrier_in VARCHAR(50),
    carrier_out VARCHAR(50),
    selling_dest VARCHAR(50),
    rule_name VARCHAR(100) NOT NULL
);

-- Create rules table for rule management
CREATE TABLE IF NOT EXISTS rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    operation VARCHAR(20) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id UUID NOT NULL,
    changed_by VARCHAR(100),
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    old_values JSONB,
    new_values JSONB
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_call_alerts_timestamp ON call_alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_call_alerts_tenant ON call_alerts(tenant);
CREATE INDEX IF NOT EXISTS idx_call_alerts_rule_name ON call_alerts(rule_name);
CREATE INDEX IF NOT EXISTS idx_call_alerts_processing_time ON call_alerts(processing_time);
CREATE INDEX IF NOT EXISTS idx_rules_name ON rules(name);
CREATE INDEX IF NOT EXISTS idx_rules_created_at ON rules(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at ON audit_log(changed_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON audit_log(table_name, record_id);

-- Grant privileges
GRANT ALL PRIVILEGES ON TABLE call_alerts TO postgres;
GRANT ALL PRIVILEGES ON TABLE rules TO postgres;
GRANT ALL PRIVILEGES ON TABLE audit_log TO postgres;