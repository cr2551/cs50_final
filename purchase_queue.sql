-- purpose of this table is to mantain a queue so that we can use the FIFO approach to calculating profits when we sell
-- stock. That is, we will calculate profit assuming we are selling the oldest purchased stocks as opposed
-- to seeling the most recently purchased stocks.
-- This table will tell us which purchase to subtract from
CREATE TABLE purchase_queue 
    (
        purchase_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE ,
        user_id INTEGER NOT NULL,
        symbol VARCHAR(255) NOT NULL,
        quantity_left INTEGER NOT NULL,
        price NUMERIC NOT NULL,
        total NUMERIC NOT NULL,
        proportional BOOLEAN DEFAULT 0, -- indicates whether we sold the same amount of shares as the corrresponding transaction
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
;