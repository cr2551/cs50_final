CREATE TABLE transactions 
    (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    symbol VARCHAR(255) NOT NULL,
    shares INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    total NUMERIC NOT NULL,
    transaction_type VARCHAR(255), -- buy or sell
    comments TEXT,
    transaction_date DATE,
    profit NUMERIC DEFAULT NULL, -- only for sales
    FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ;