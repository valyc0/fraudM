CREATE TABLE calls_stream (
    `event_type` STRING,
    `kafka_timestamp` TIMESTAMP_LTZ(3) METADATA FROM 'timestamp',
    `carrier_out` STRING,
    `@timestamp` TIMESTAMP_LTZ(3),
    `tenant` STRING,
    `economicUnitValue` DOUBLE,
    `selling_dest` STRING,
    `paese_destinazione` STRING,
    `event_timestamp` TIMESTAMP_LTZ(3),
    `routing_dest` STRING,
    `duration` INT,
    `val_euro` DOUBLE,
    `raw_called_number` STRING,
    `raw_caller_number` STRING,
    `carrier_in` STRING,
    `xdrid` STRING,
    `other_party_country` STRING,
    WATERMARK FOR `event_timestamp` AS `event_timestamp` - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'call-data-raw',
    'properties.bootstrap.servers' = 'kafka:29092',
    'properties.group.id' = 'flink-rule-group',
    'format' = 'json',
    'json.timestamp-format.standard' = 'ISO-8601',
    'json.fail-on-missing-field' = 'false',
    'json.ignore-parse-errors' = 'true',
    'scan.startup.mode' = 'earliest-offset',
    'properties.fetch.min.bytes' = '1048576',
    'properties.fetch.max.wait.ms' = '10000'
);

CREATE TABLE call_alerts (
    xdrid STRING,
    tenant STRING,
    val_euro DOUBLE,
    duration INT,
    raw_caller_number STRING,
    raw_called_number STRING,
    `timestamp` TIMESTAMP_LTZ(3),
    event_time TIMESTAMP_LTZ(3),
    carrier_in STRING,
    carrier_out STRING,
    selling_dest STRING,
    rule_name STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'call-alerts',
    'properties.bootstrap.servers' = 'kafka:29092',
    'format' = 'json',
    'json.timestamp-format.standard' = 'ISO-8601'
);

INSERT INTO call_alerts
SELECT
    xdrid,
    tenant,
    val_euro,
    duration,
    raw_caller_number,
    raw_called_number,
    kafka_timestamp AS `timestamp`,
    event_timestamp AS event_time,
    carrier_in,
    carrier_out,
    selling_dest,
    'simple_copy_rule' AS rule_name
FROM calls_stream;