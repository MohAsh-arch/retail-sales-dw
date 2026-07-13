from datetime import timedelta ,date
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from db_utils import insertion, empty_check, get_list_of_column , db_connect



conn = db_connect()
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


#--- dim_product 
if empty_check(conn,cur,'dw.dim_product'):
    cur.execute("SELECT p.product_id," \
    " c.category_id," \
    " c.category_name," \
    " p.name," \
    " p.price from" \
    " product p " \
    "join category c " \
    "on p.category_id = c.category_id")

    product_oltp_tuples = cur.fetchall()
    valid_from = date.today()
    product_olap_tuples = []
    for ptuple in product_oltp_tuples:
        ptuple += (valid_from,)
        ptuple += (None,)
        ptuple += (True,)
        product_olap_tuples.append(ptuple)
    
    dim_product_ins_column = 'product_id,category_id,category_name,name,price,valid_from,valid_to,is_current'
    insertion(conn,cur,'dw.dim_product',dim_product_ins_column, product_olap_tuples,on_conflict=False)

conn.commit()

