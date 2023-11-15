SELECT 
    symbol
    SUM(CASE WHEN transaction_type='buy' THEN shares ELSE -shares END) AS quantity
    
