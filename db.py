from cs50 import SQL
import time
import os
from dotenv import load_dotenv
import sys


print('python version: ', sys.version)
# ouput = os.popen('/opt/render/project/src/.venv/bin/python -m pip install --upgrade pip').read()
# print(ouput)

load_dotenv()

url = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://', 1)
internal_url = os.getenv('INTERNAL_DB_URL').replace('postgres://', 'postgresql://', 1)

# db = SQL(internal_url)
db = SQL(url)

def test_table():
    query = 'CREATE TABLE test_hi (num INT);'
    db.execute(query)



def create_tables():

    with open('./initialize_db_psql.sql', 'r') as schema:
        queries = schema.read()
        queries = queries.split(';') 
        for q in queries:
            if q.strip():
                print(q)
                db.execute(q)
                # time.sleep(1)
    


def drop_tables():
    with open('./drop_tables.sql', 'r') as drop:
        queries = drop.read()
        queries = queries.split(';')
        print(queries)
        for q in queries:
            if q.strip():
                db.execute(q)

def print_tables():
    tables = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    for t in tables:
        print(t)

def users():
    users = db.execute('SELECT * FROM users;')
    transactions = db.execute('SELECT * FROM transactions;')
    purchases = db.execute('SELECT * FROM purchase_queue;')
    
    print(users, transactions, purchases)
    
drop_tables()
create_tables()
test_table()
print_tables()
users()

