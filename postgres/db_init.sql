-- Create table for call alerts
CREATE TABLE IF NOT EXISTS call_alerts (
    xdrid VARCHAR(36) PRIMARY KEY,
    tenant VARCHAR(50),
    val_euro DECIMAL(10,2),
    duration INTEGER,
    raw_caller_number VARCHAR(20),
    raw_called_number VARCHAR(20),
    timestamp TIMESTAMP,
    event_time TIMESTAMP,
    carrier_in VARCHAR(50),
    carrier_out VARCHAR(50),
    selling_dest VARCHAR(50)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_call_alerts_timestamp ON call_alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_call_alerts_tenant ON call_alerts(tenant);

-- Grant privileges
GRANT ALL PRIVILEGES ON TABLE call_alerts TO postgres;