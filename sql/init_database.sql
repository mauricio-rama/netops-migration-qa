CREATE SCHEMA IF NOT EXISTS source_system;
CREATE SCHEMA IF NOT EXISTS target_system;

CREATE TABLE IF NOT EXISTS source_system.customers (
    customer_id BIGINT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS target_system.customers (
    customer_id BIGINT PRIMARY KEY,
    full_name VARCHAR(201) NOT NULL,
    email VARCHAR(255),
    customer_status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    migration_timestamp TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS source_system.customers_staging (
    customer_id BIGINT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    status VARCHAR(20),
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS source_system.customer_orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT,
    order_amount NUMERIC(12,2),
    order_date TIMESTAMP
);

INSERT INTO source_system.customers
    (customer_id, first_name, last_name, email, status, created_at)
VALUES
    (100001, 'Mauricio', 'Ramirez', 'mauricio@example.com', 'ACTIVE', '2026-01-10 09:15:00'),
    (100002, 'Laura', 'Garcia', 'laura@example.com', 'ACTIVE', '2026-01-11 10:30:00'),
    (100003, 'Carlos', 'Martinez', 'carlos@example.com', 'INACTIVE', '2026-01-12 11:45:00'),
    (100004, 'Ana', 'Lopez', 'ana@example.com', 'ACTIVE', '2026-01-13 08:20:00'),
    (100005, 'Jorge', 'Hernandez', 'jorge@example.com', 'ACTIVE', '2026-01-14 14:10:00');

INSERT INTO target_system.customers
    (customer_id, full_name, email, customer_status, created_at, migration_timestamp)
SELECT
    customer_id,
    first_name || ' ' || last_name,
    email,
    status,
    created_at,
    CURRENT_TIMESTAMP
FROM source_system.customers;

INSERT INTO source_system.customers_staging
    (customer_id, first_name, last_name, email, status, created_at)
SELECT
    customer_id,
    first_name,
    last_name,
    email,
    status,
    created_at
FROM source_system.customers;

INSERT INTO source_system.customer_orders
    (order_id, customer_id, order_amount, order_date)
VALUES
    (500001, 100001, 1250.00, '2026-02-01 10:00:00');