-- Rule: trova un caller che chiama piu di 3 caller nell'arco di 2 minuti

-- Create Kafka source table
CREATE TABLE calls_stream (
    tenant STRING,
    val_euro DOUBLE,
    duration BIGINT,
    economicUnitValue DOUBLE,
    other_party_country STRING,
    routing_dest STRING,
    service_type__desc STRING,
    op35 STRING,
    carrier_in STRING,
    carrier_out STRING,
    selling_dest STRING,
    raw_caller_number STRING,
    raw_called_number STRING,
    paese_destinazione STRING,
    event_time TIMESTAMP(3),
    xdrid STRING,
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'call-data-raw',
    'properties.bootstrap.servers' = 'kafka:29092',
    'properties.group.id' = 'flink-rule-group',
    'format' = 'json',
    'json.fail-on-missing-field' = 'false',
    'json.ignore-parse-errors' = 'true',
    'scan.startup.mode' = 'latest-offset',
    'properties.fetch.min.bytes' = '1048576',
    'properties.fetch.max.wait.ms' = '10000'
);

-- Create OpenSearch sink table for alerts
CREATE TABLE alerts (
    rule STRING,
    caller STRING,
    distinct_called_count BIGINT,
    tenant STRING,
    val_euro DOUBLE,
    duration BIGINT,
    economicUnitValue DOUBLE,
    other_party_country STRING,
    routing_dest STRING,
    service_type__desc STRING,
    carrier_in STRING,
    carrier_out STRING,
    selling_dest STRING,
    paese_destinazione STRING,
    xdrid STRING,
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    PRIMARY KEY (caller, window_start) NOT ENFORCED
) WITH (
    'connector' = 'elasticsearch-7',
    'hosts' = 'http://opensearch:9200',
    'username' = 'admin',
    'password' = 'admin',
    'index' = 'flink-alerts',
    'format' = 'json',
    'sink.bulk-flush.max-actions' = '1',
    'sink.flush-on-checkpoint' = 'true'
);

-- Insert into alerts when a caller calls more than 3 different numbers in 2 minutes
INSERT INTO alerts
SELECT
    'Caller chiamati > 3 in 2 minuti' as rule,
    raw_caller_number as caller,
    COUNT(DISTINCT raw_called_number) as distinct_called_count,
    MAX(tenant) as tenant,
    SUM(COALESCE(TRY_CAST(val_euro AS DOUBLE), 0)) as val_euro,
    SUM(duration) as duration,
    SUM(COALESCE(TRY_CAST(economicUnitValue AS DOUBLE), 0)) as economicUnitValue,
    MAX(other_party_country) as other_party_country,
    MAX(routing_dest) as routing_dest,
    MAX(service_type__desc) as service_type__desc,
    MAX(carrier_in) as carrier_in,
    MAX(carrier_out) as carrier_out,
    MAX(selling_dest) as selling_dest,
    MAX(paese_destinazione) as paese_destinazione,
    MAX(xdrid) as xdrid,
    window_start,
    window_end
FROM TABLE(
    TUMBLE(TABLE calls_stream, DESCRIPTOR(event_time), INTERVAL '2' MINUTES)
)
GROUP BY 
    raw_caller_number,
    window_start,
    window_end
HAVING 
    COUNT(DISTINCT raw_called_number) > 3;