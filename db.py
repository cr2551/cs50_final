from cs50 import SQL
import time
import os

url = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://', 1)
db = SQL(url)



def create_tables():

    with open('./initialize_db_psql.sql', 'r') as schema:
        queries = schema.read()
        queries = queries.split(';') 
        for q in queries:
            if q.strip():
                db.execute(q)
                time.sleep(1)
    


def drop_tables():
    with open('./drop_tables.sql', 'r') as drop:
        queries = drop.read()
        queries = queries.split(';')
        print(queries)
        for q in queries:
            if q.strip():
                # print('1')
                db.execute(q)

def print_tables():
    tables = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    for t in tables:
        print(t)

def users():
    users = db.execute('SELECT * FROM transactions;')
    print(users)
    
# drop_tables()
# create_tables()
print_tables()
users()

