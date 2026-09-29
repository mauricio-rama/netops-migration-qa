CREATE TABLE IF NOT EXISTS migration_control (
    pipeline_name VARCHAR(100) PRIMARY KEY,
    last_processed_timestamp TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS source_system.customers_incremental (
    customer_id BIGINT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    status VARCHAR(20) NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS target_system.customers_incremental (
    customer_id BIGINT PRIMARY KEY,
    full_name VARCHAR(201) NOT NULL,
    email VARCHAR(255),
    customer_status VARCHAR(20) NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    migration_timestamp TIMESTAMP NOT NULL
);
