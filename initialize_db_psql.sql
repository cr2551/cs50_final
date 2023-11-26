-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 0
);
    -- Create portfolios table
CREATE TABLE portfolios (
    user_id INTEGER REFERENCES users(id),
    symbol VARCHAR(255) NOT NULL,
    shares NUMERIC NOT NULL,
    price FLOAT NOT NULL,
    gain_loss NUMERIC NOT NULL,
    PRIMARY KEY (user_id, symbol)
);

-- Create transactions table
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol VARCHAR(255) NOT NULL,
    shares INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    total NUMERIC NOT NULL,
    transaction_type VARCHAR(255),
    comments TEXT,
    transaction_date DATE,
    profit NUMERIC DEFAULT NULL,
    dequeued BOOLEAN DEFAULT FALSE,
    FOREIGN KEY(user_id) REFERENCES users(id)
);


-- Create purchase_queue table
CREATE TABLE purchase_queue (
    purchase_id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL,
    user_id INTEGER REFERENCES users(id),
    symbol VARCHAR(255) NOT NULL,
    quantity_left INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    total NUMERIC NOT NULL,
    proportional BOOLEAN DEFAULT FALSE, -- changed to FALSE as BOOLEAN does not use 0 or 1 in PostgreSQL
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(transaction_id) REFERENCES transactions(transaction_id)
);


