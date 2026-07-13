import  psycopg2 
import os
from dotenv import load_dotenv
from db_utils import insertion, empty_check, get_list_of_column , db_connect
import random
from faker import Faker
from faker_commerce import Provider
from collections import defaultdict



random.seed(42)
Faker.seed(42)

conn = db_connect()

cur = conn.cursor()





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
    insertion(conn, cur, 'regions' , 'name' , regions ,  on_conflict=True ,conflict_column="name")

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
    insertion(conn , cur , 'category', 'category_name', categories ,on_conflict=True,conflict_column='category_name' )

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



    insertion(conn, cur, 'branch' , 'city , region_id' , branch_insert_tuples ,on_conflict=False)

fake = Faker()
#--- product insertion ---
fake.add_provider(Provider)
product_insert_tuples = []
categ_id_list = get_list_of_column(cur,'category','category_id')


if empty_check(conn, cur, 'product'):
    for i in range(500):
        prod_categ = random.choice(categ_id_list)
        prod_name = fake.ecommerce_name()
        prod_price = round(random.uniform(5, 2000),2)
        product_insert_tuples.append((prod_categ,prod_name,prod_price))

    insertion(conn , cur , 'product', 'category_id , name , price' , product_insert_tuples ,on_conflict=True,conflict_column='name')

#--- customer insertion ---

if empty_check(conn,cur,'customer'):
    customer_insert_tuples = []
    for i in range (10_500):
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone = fake.phone_number()
        email = fake.email()
        address = fake.address()
        customer_insert_tuples.append((first_name,last_name,phone,email,address))
    customer_insert_column = 'first_name , last_name, phone, email, address'
    insertion(conn ,cur, 'customer', customer_insert_column , customer_insert_tuples, on_conflict=True, conflict_column='email' )


#--- employee insertion ---

if empty_check(conn,cur,'employee'): 
    employee_insert_tuples = []
    branch_id_list = get_list_of_column(cur,'branch','branch_id')

    for id in branch_id_list:
        no_of_emp = random.randint(15,20)
        for i in range(no_of_emp):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()
            branch_emp_id = id
            employee_insert_tuples.append((first_name,last_name,email,branch_emp_id))

    employee_insert_column = 'first_name,last_name,email,branch_id'
    insertion(conn ,cur, 'employee', employee_insert_column , employee_insert_tuples, on_conflict=True, conflict_column='email' )

#--- orders insertion --- 
if empty_check(conn,cur,'orders'):
    branch_id_list = get_list_of_column(cur,'branch','branch_id')

    customer_id_list = get_list_of_column(cur,'customer','customer_id')

    cur.execute('SELECT branch_id , employee_id FROM employee')
    list_of_branch_emp_tuples = cur.fetchall()
    dict_branch_emp_id = dict()

    for key, value in list_of_branch_emp_tuples:
        if key not in dict_branch_emp_id:
            dict_branch_emp_id[key] = []
        dict_branch_emp_id[key].append(value)

    orders_insert_tuples = []
    for i in range(75000):
        orders_branch_id = random.choice(branch_id_list)
        orders_employee_id = random.choice(dict_branch_emp_id[orders_branch_id])
        order_timestamp = fake.date_time_between( start_date='-1y',end_date='now')
        orders_customer = random.choice(customer_id_list)
        orders_insert_tuples.append((orders_customer,order_timestamp,orders_branch_id,orders_employee_id))
    
    orders_insertion_columns = 'customer_id , order_timestamp , branch_id , employee_id'
    insertion(conn,cur,'orders',orders_insertion_columns, orders_insert_tuples , on_conflict=False)

#--- orders insertion --- 
if empty_check(conn,cur, 'order_items'):
    items_list_tuples = []
    order_id_list = get_list_of_column(cur,'orders' , 'order_id')
    product_id_list = get_list_of_column(cur,'product' , 'product_id')
    cur.execute('SELECT product_id, price FROM product')
    list_of_prod_price_tuples = cur.fetchall()
    product_id_price_dict = dict(list_of_prod_price_tuples)



    for order_id in order_id_list:
        items_per_order = random.randint(1,5)
        for i in range(items_per_order):
            item_product_id = random.choice(product_id_list)
            item_quantity = random.randint(1,10)
            item_unit_price = product_id_price_dict[item_product_id]
            items_list_tuples.append((order_id,item_product_id,item_quantity,item_unit_price))
    items_insertion_column = 'order_id,product_id,quantity,unit_price'
    insertion(conn,cur,'order_items',items_insertion_column, items_list_tuples , on_conflict=True,conflict_column='order_id, product_id')





conn.commit() # saving the changes
print("all works")