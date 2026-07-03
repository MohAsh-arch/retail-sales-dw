import  psycopg2 
import os
from dotenv import load_dotenv
from psycopg2.extras import execute_values
import random
from faker import Faker
from faker_commerce import Provider



random.seed(42)
Faker.seed(42)

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





def empty_check(conn, cursor , table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    if count == 0:
        return True
    else: 
        return False
        

def insertion(conn , cursor, table_name, insert_column, values, pk_column, on_conflict = True,conflict_column=''):
    if on_conflict:
        query = f"""INSERT INTO {table_name} ({insert_column}) VALUES %s
                    ON CONFLICT ({conflict_column}) DO NOTHING"""
    else:
        query = f"""INSERT INTO {table_name} ({insert_column}) VALUES %s"""
    # saving by batches 
    execute_values(cursor, query, values)

    cursor.execute(f"SELECT {pk_column} FROM {table_name}")
    result_tuple = cursor.fetchall()
    result_list = [row[0] for row in result_tuple]

    return result_list


#--- region insertion ---
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

if empty_check(conn, cur, 'regions'):
    regions_list = insertion(conn, cur, 'regions' , 'name' , regions , 'region_id', on_conflict=True ,conflict_column="name")

#--- category insertion ---
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

if empty_check(conn, cur, 'category'):
    categories_list = insertion(conn , cur , 'category', 'category_name', categories , 'category_id', on_conflict=True,conflict_column='category_name' )

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

fake = Faker()
#--- product insertion ---
fake.add_provider(Provider)
product_insert_tuples = []
cur.execute('SELECT category_id FROM category')
categ_id_tuples = cur.fetchall()
categ_id_list = [id[0] for id in categ_id_tuples]


if empty_check(conn, cur, 'product'):
    for i in range(500):
        prod_categ = random.choice(categ_id_list)
        prod_name = fake.ecommerce_name()
        prod_price = round(random.uniform(5, 2000),2)
        product_insert_tuples.append((prod_categ,prod_name,prod_price))

    insertion(conn , cur , 'product', 'category_id , name , price' , product_insert_tuples , 'product_id',on_conflict=True,conflict_column='name')

#--- customer insertion ---
customer_insert_tuples = []
if empty_check(conn,cur,'customer'):
    for i in range (10_500):
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone = fake.phone_number()
        email = fake.email()
        address = fake.address()
        customer_insert_tuples.append((first_name,last_name,phone,email,address))
    customer_insert_column = 'first_name , last_name, phone, email, address'
    insertion(conn ,cur, 'customer', customer_insert_column , customer_insert_tuples, 'customer_id', on_conflict=True, conflict_column='email' )



conn.commit() # saving the changes
