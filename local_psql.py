# connect to local psql instance to conduct tests
import sqlalchemy
import psycopg2
from cs50 import SQL


db_url = 'postgresql+psycopg2://crod:1389@localhost:5432/mylaptop'
db = SQL(db_url)
r = db.execute('SELECT * FROM hi')
print(r)
# engine = sqlalchemy.create_engine(db_url)

# connection = engine.connect()
# query = sqlalchemy.text("SELECT * FROM information_schema.tables WHERE table_schema = 'public'")
# results = connection.execute(query)
# for i in results:
#     print(i)

# connection.close()