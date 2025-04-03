
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
    event_time TIMESTAMP(3) METADATA FROM 'timestamp',
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
    'scan.startup.mode' = 'earliest-offset'
);

CREATE TABLE call_alerts (
    xdrid STRING,
    tenant STRING,
    val_euro DOUBLE,
    duration INT,
    raw_caller_number STRING,
    raw_called_number STRING,
    `timestamp` TIMESTAMP(3),
    event_time TIMESTAMP(3),
    carrier_in STRING,
    carrier_out STRING,
    selling_dest STRING,
    rule_name STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'call-alerts',
    'properties.bootstrap.servers' = 'kafka:29092',
    'format' = 'json'
);

INSERT INTO call_alerts
SELECT
    MAX(xdrid),
    tenant,
    SUM(val_euro),
    CAST(SUM(duration) AS INT),
    raw_caller_number,
    'MULTIPLE' AS raw_called_number,
    CURRENT_TIMESTAMP as `timestamp`,
    MAX(event_time),
    MAX(carrier_in),
    MAX(carrier_out),
    MAX(selling_dest),
    'high_frequency_caller' AS rule_name
FROM calls_stream
GROUP BY TUMBLE(event_time, INTERVAL '10' MINUTE), tenant, raw_caller_number
HAVING COUNT(DISTINCT raw_called_number) > 10
