# Portfolio Tracker

This is a portfolio tracker. Its purpose is to show you how your investments are performing at a glance compared to your initial expectations.

#### Video Demo:
<https://youtu.be/elKTg0OW574>

In the Add Transactions tab you'll see a form where you can input the stocks the info about a purchase or sale you've made.
Moreover, there is an extra field in which you can write your thoughts about the transaction, why you took this decision, and in the case of purchases where you think the investment will go and why.
In this fashion you can keep track of your investment strategy and thought process, and in the future, compare it to the actual performance of the stock.

Once you have added your transaction you will be taken to the History tab where you will see a table with your most recent transaction at the bottom.

Each transaction has a link that will take you to a page displaying your comments if any, and a text box icon will be displayed for those transactions that have comments.

You will also notice a colum in the table called 'Profit'. Here the profit from selling stock is calculated using a First In First Out approach or FIFO. But more on that in the Implementation section. The profit column is also colored depending if the sale result in a profit or loss.

Additionally, the table can be ordered by Date and by Profit by clicking on the column headers.

After you've recorded your first transaction you can head over to the Portfolio tab. Here you can see the details of your portfolio holdings. For each position, you will be able to see:

- shares you own
- the average price per share
- current price
- percentage return (unrealized gains)
- portfolio diversity (percentage that this position represents of your portfolio)
- gains (returns in dollar amount)
- total value of position

Here the average price is calculated by using a weighted average of the stocks you own. And the gains are also obained using this calculation.
In this way they match closely what you would see in the profit column in the history table.

The 'return' and 'gains' columns change color appropriately depending on wether the returns are positive or not.
This Table can also be sorted by the percentage returns and the gains by clicking on the column headers.

## Implementation

This is a web app using flask, jinja templates, sqlite3 and bootstrap.
there is an sql table to store user info, another to store a history of all transactions, and one more to serve as queue to know which stocks to sell next.

One of the first major desing decisions was how to calculate the profit/loss of a sale. Which may not be as straightforward as it seems. Take for example, if a user buys 3 shares of a stock and sells them the next day we could say their profit is just the SaleTotal - PurchaseTotal. Howerver if a user buys different amounts of shares at different times and prices poins, then we must choose a way to calculate the profits.

 In my case, I opted to use a First In First Out approach, where we sell the oldest shares in our possesion. In this way, each time the user wanted to make a sale there should be a correponding purchase transaction, namely the first element in the queue.

 Therefore, I needed a way to keep track of the queue. And to use it to complete the sale and accurately calculate the profit when the user wanted to sell less or more than the amount that was purchased in the corresponding transaction.

 My approach was to store each purchase on an sql database. Then when a sale was requested, I would use a for loop to iterate over the rows of the database and handle all cases where the number of shares being sold are greater, equal, or lesser than the corresponding transaction.

 The for loop is necessary to delete the purchase transaction from the queue and go
 on to the next one as many times as necessary and to calculate the purchaseTotal that will be subtractred from the SaleTotal and thus obtain our profit.

 Once I had a record of which stocks had been sold, I could calculate a weighted average cost of each stock that would not take into account the cost of the stocks we had already sold. This weighted average cost per share was then used the returns shown in the portfolio table.

 The portfolio table is obtained by making a select query from the transactions table to obtain the amount of stocks we own. Then for each stock we query for the price to calculate the average price we paid for those stocks and the rest of the calculations are made using the current price and the results are added as keys on a dictionary, those dictionaries will in turn be stored in a list named 'portfolio'
 which will be one of the return values of the 'get_portfolio()' function defined in helpers.py.

 I also wanted to be able to sort the tables by certain columns. And here I found two approaches with their respective pros and cons.

 1. Use ORDER BY in a select statement
    or
 2. Use the sorted() python function to sort the list of dictionaries by a certain key.

I used the second approach for the portfolio table since there is no portfolio sql table. The portfolio is constructed on the fly because all of the values need to be recalculated on every refresh. It's disadvantage is that you potentially have to deal with comparing object of different types in which you might get an error. This is not difficult to overcome using python's filter function to only soert the values of a certain type. However, it doesn't look too clean and might require long comments to explain why it is needed.

The first approach eliminates the ability to do input sanitation with a placeholder, so it is up to you to do so. On the other hand, sql manages the ordering for you. In the case of the Date column for example, sql can order the table based on those dates even for rows that have no date in them.

## Conclusions

In this final project for the cs50 course I increased my knowledge and comfort with flask and bootstrap, I gained more experience controlling sql using python. Overall I feel like this project sharpened and refined my skills.
