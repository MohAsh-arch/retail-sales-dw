import psycopg2
import os 
from dotenv import load_dotenv
from datetime import timedelta
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from db_utils import insertion, empty_check, get_list_of_column

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


#---- dim_time population ---

cur.execute('select min(order_timestamp) , max(order_timestamp) from orders')
min , max = cur.fetchone()
min_date = min.date()
max_date = max.date()


current = min_date
if empty_check(conn,cur,'dw.dim_time'):
    dim_time_tuples  = []
    while current <= max_date:
        full_date = int(current.strftime('%Y%m%d')) # formating the string to match the date_key base 
        month = current.month
        year = current.year
        week = current.isocalendar()[1] # as isocalender() returns a tuple of (year , week , weekday)
        quarter = (month - 1) // 3 + 1
        dim_time_tuples.append((full_date,current,week,month,year,quarter))
        current += timedelta(days=1)
    dim_time_ins_columns = ' date_key, full_date, week, month, year, quarter'
    insertion(conn,cur,'dw.dim_time',dim_time_ins_columns, dim_time_tuples , on_conflict=True, conflict_column='date_key')

#--- dim_employee poplution ---
if empty_check(conn,cur,'dw.dim_employee'):
    cur.execute('select employee_id , first_name , last_name , email from employee')
    dim_employee_tuples = cur.fetchall()
    dim_emp_ins_cols = 'employee_id , first_name , last_name , email' 
    insertion(conn,cur,'dw.dim_employee',dim_emp_ins_cols,dim_employee_tuples,on_conflict=False)

#--- dim_barnch population ---
if empty_check(conn,cur,'dw.dim_branch'):
    cur.execute('select b.branch_id ,' \
    ' b.city ,' \
    ' r.region_id ,' \
    ' r.name' \
    ' from branch b' \
    ' join regions r on ' \
    'b.region_id = r.region_id')
    dim_branch_tuples = cur.fetchall()
    dim_bra_ins_cols = 'branch_id , city, region_id , region_name' 
    insertion(conn,cur,'dw.dim_branch',dim_bra_ins_cols,dim_branch_tuples,on_conflict=False)


#--- dim_customer ---

if empty_check(conn,cur,'dw.dim_customer'):
    cur.execute('SELECT customer_id, first_name, last_name, phone, email, address FROM customer')
    dim_customer_tuples = cur.fetchall()
    dim_customer_ins_cols = 'customer_id,first_name,last_name,phone, email,address'
    insertion(conn,cur,'dw.dim_customer', dim_customer_ins_cols, dim_customer_tuples, on_conflict=False)

conn.commit()