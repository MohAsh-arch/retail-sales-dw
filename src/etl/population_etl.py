from datetime import timedelta ,date
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from db_utils import insertion, empty_check, get_list_of_column , db_connect , key_id



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

#--- fact_retail population ---

if empty_check(conn,cur,'dw.fact_retail'):
    product_key_id = key_id(cur,'product_id','product_key','dw.dim_product','WHERE is_current = True')
    branch_key_id = key_id(cur,'branch_id','branch_key','dw.dim_branch')
    customer_key_id = key_id(cur,'customer_id','customer_key','dw.dim_customer')
    employee_key_id = key_id(cur,'employee_id','employee_key','dw.dim_employee')

    cur.execute(''' SELECT  o.order_id,
                            o.customer_id,
                            o.order_timestamp,
                            o.branch_id,
                            o.employee_id,
                            oi.product_id,
                            oi.quantity,
                            oi.unit_price
                FROM orders o join 
                order_items oi on o.order_id = oi.order_id
    ''')

    join_list_of_tuples = cur.fetchall()
    fact_list_of_tuples = []

    for tuple_ in join_list_of_tuples:
        product_key = product_key_id[tuple_[5]]
        branch_key = branch_key_id[tuple_[3]]
        customer_key = customer_key_id[tuple_[1]]
        employee_key = employee_key_id.get(tuple_[4]) # i use get method here because it return none and employee_id are nullable which will not produce an error because regular method will return empty
        order_id = tuple_[0]
        quantity = tuple_[6]
        date_key = int(tuple_[2].strftime("%Y%m%d"))
        fact_list_of_tuples.append((date_key,product_key,branch_key,customer_key,employee_key,order_id,quantity,tuple_[7]))
    insert_columns = 'date_key, product_key, branch_key, customer_key, employee_key, order_id, quantity, unit_price'
    insertion(conn, cur,'dw.fact_retail',insert_columns,fact_list_of_tuples,on_conflict=False)




conn.commit()

