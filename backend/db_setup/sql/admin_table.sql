CREATE TABLE IF NOT EXISTS admin (
    uid VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(100),
    address TEXT,
    mobile_num VARCHAR(15),
    email VARCHAR(100),
    valid_id_numbers JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at JSON,
    password CHAR(64),
    username VARCHAR(50) UNIQUE
);
