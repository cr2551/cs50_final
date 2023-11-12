CREATE TABLE portfolios
    (user_id, 
    symbol VARCHAR(255) NOT NULL,
    shares NUMERIC NOT NULL, -- allow for fractional shares
    price FLOAT NOT NULL,
    gain_loss NUMERIC NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
    )