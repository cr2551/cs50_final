-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 0
);
 
-- Create transactions table
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(255) NOT NULL,
    shares INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    total NUMERIC NOT NULL,
    transaction_type VARCHAR(255),
    comments TEXT,
    transaction_date DATE,
    profit NUMERIC DEFAULT NULL,
    dequeued BOOLEAN DEFAULT false
);

    -- FOREIGN KEY(user_id) REFERENCES users(id)

-- Create purchase_queue table
CREATE TABLE purchase_queue (
    purchase_id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL,
    user_id INTEGER,
    symbol VARCHAR(255) NOT NULL,
    quantity_left INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    total NUMERIC NOT NULL,
    proportional BOOLEAN DEFAULT false,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE
);


