import  psycopg2 
import os
from dotenv import load_dotenv
from psycopg2.extras import execute_values


load_dotenv()

try : 
    conn = psycopg2.connect(
        host="localhost",
        port=int(os.environ["DB_PORT"]),
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"]
        )
    
    print("connection successfully ")
except Exception as e:
    print(f"couldn't connect to the database because : {e}") 

cur = conn.cursor()

regions = [
    ("Andes",),
    ("Alps",),
    ("Sahara",),
    ("Gobi",),
    ("Crimea",),
    ("Punjab",),
    ("Balkans",),
    ("Siberia",),
    ("Baltics",),
    ("Levant",)
]

query_region = """INSERT INTO regions (name) VALUES %s
                  ON CONFLICT (name) DO NOTHING"""
# saving by batches 
execute_values(cur, query_region, regions)

cur.execute("SELECT region_id FROM regions")
ids = cur.fetchall()
conn.commit() # saving the changes
ids_list = [row[0] for row in ids]

print(ids_list)