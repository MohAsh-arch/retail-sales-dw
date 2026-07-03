import  psycopg2 
import os
from dotenv import load_dotenv
from psycopg2.extras import execute_values
import random

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

# creating the regions table

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
# Creating the category table 
categories = [
    ("Women's Clothing",),
    ("Men's Clothing",),
    ("Furniture",),
    ("Kitchen & Dining",),
    ("Computers & Tablets",),
    ("Mobile & Wearables",),
    ("Personal Care",),
    ("Skincare & Cosmetics",),
    ("Pantry & Dry Goods",),
    ("Beverages",),
    ("Toys & Games",),
    ("Pet Supplies",)
]


def empty_check(conn, cursor , table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    if count == 0:
        return True
    else: 
        return False
        

def insertion(conn , cursor, table_name, insert_column, values, pk_column, on_conflict = True):
    if on_conflict:
        query = f"""INSERT INTO {table_name} ({insert_column}) VALUES %s
                    ON CONFLICT ({insert_column}) DO NOTHING"""
    else:
        query = f"""INSERT INTO {table_name} ({insert_column}) VALUES %s"""
    # saving by batches 
    execute_values(cursor, query, values)

    cursor.execute(f"SELECT {pk_column} FROM {table_name}")
    result_tuple = cursor.fetchall()
    result_list = [row[0] for row in result_tuple]

    return result_list

regions_list = insertion(conn, cur, 'regions' , 'name' , regions , 'region_id')
categories_list = insertion(conn , cur , 'category', 'category_name', categories , 'category_id')

#---
#--- creating the branch table ---

cur.execute('SELECT name , region_id FROM regions')
regions_dict = dict(cur.fetchall())

region_city_map = {
    "Andes": ["Bogotá", "Cusco"],
    "Alps": ["Geneva", "Innsbruck"],
    "Sahara": ["Cairo", "Khartoum"],
    "Gobi": ["Ulaanbaatar", "Hohhot"],
    "Crimea": ["Sevastopol", "Yalta"],
    "Punjab": ["Lahore", "Amritsar"],
    "Balkans": ["Belgrade", "Sofia"],
    "Siberia": ["Novosibirsk", "Irkutsk"],
    "Baltics": ["Riga", "Tallinn"],
    "Levant": ["Beirut", "Amman"]
}


if empty_check(conn,cur,'branch'):
    region_city_id_map = dict()
    for key , value in regions_dict.items() : 
        region_city_id_map[value] = region_city_map[key] 


    branch_insert_tuples = []

    for id , cities in region_city_id_map.items():
        no_of_branches = random.randint(3,5)
        for i in range(no_of_branches):
            city = random.choice(cities)
            branch_insert_tuples.append((city,id))



    insertion(conn, cur, 'branch' , 'city , region_id' , branch_insert_tuples , 'branch_id', on_conflict=False)





print(empty_check(conn, cur, 'branch'))






conn.commit() # saving the changes
