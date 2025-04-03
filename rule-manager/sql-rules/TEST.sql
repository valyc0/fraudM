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

-- Example query to extract all fields with proper timestamps
SELECT
    event_type,
    kafka_timestamp,
    carrier_out,
    @timestamp,
    tenant,
    economicUnitValue,
    selling_dest,
    paese_destinazione,
    event_timestamp,
    routing_dest,
    duration,
    val_euro,
    raw_called_number,
    raw_caller_number,
    carrier_in,
    xdrid,
    other_party_country
FROM calls_stream;