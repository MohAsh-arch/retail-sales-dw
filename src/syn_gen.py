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


def insertion(conn , cursor, table_name, insert_column, values, pk_column):

    query = f"""INSERT INTO {table_name} ({insert_column}) VALUES %s
                    ON CONFLICT ({insert_column}) DO NOTHING"""
    # saving by batches 
    execute_values(cursor, query, values)

    cursor.execute(f"SELECT {pk_column} FROM {table_name}")
    result_tuple = cursor.fetchall()
    result_list = [row[0] for row in result_tuple]

    return result_list

regions_list = insertion(conn, cur, 'regions' , 'name' , regions , 'region_id')
categories_list = insertion(conn , cur , 'category', 'category_name', categories , 'category_id')

print(regions_list)
print(categories_list)


























conn.commit() # saving the changes
