CREATE TABLE IF NOT EXISTS host_participant (
    uid VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100),
    mobile_num VARCHAR(15),
    address TEXT,
    location VARCHAR(100),
    hosting_addresses JSON,
    locality JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at JSON,
    password CHAR(64),
    username VARCHAR(50) UNIQUE,
    ranged_id INT UNIQUE
);
