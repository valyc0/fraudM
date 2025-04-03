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

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_call_alerts_timestamp ON call_alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_call_alerts_tenant ON call_alerts(tenant);
CREATE INDEX IF NOT EXISTS idx_call_alerts_rule_name ON call_alerts(rule_name);
CREATE INDEX IF NOT EXISTS idx_call_alerts_processing_time ON call_alerts(processing_time);

-- Grant privileges
GRANT ALL PRIVILEGES ON TABLE call_alerts TO postgres;