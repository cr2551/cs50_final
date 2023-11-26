from cs50 import SQL
import requests
import sqlite3
import psycopg2
import time

db = SQL('postgresql://project_irug_user:5l1wHrMhhXfg43dQ8z6G83ZkOoK3zvCb@dpg-clha696bbf9s73b0bhu0-a.oregon-postgres.render.com/project_irug')


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
    
# drop_tables()
# create_tables()
print_tables()

