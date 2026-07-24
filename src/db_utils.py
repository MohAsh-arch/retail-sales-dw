from psycopg2.extras import execute_values
import psycopg2
import os 
from dotenv import load_dotenv

def db_connect():
    """Establishs a connection to the database in docker 

    Return : the connection varialbe conn 
    """
    load_dotenv()

    try : 
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ["DB_PORT"]),
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"]
            )
        
        print("connection successfully ")
        return conn
    except Exception as e:
        print(f"couldn't connect to the database because : {e}") 



def get_list_of_column(cur,table_name ,column_name):
    """Get a column from the database and transform it into list 
    
    Arguments
    cur: An open psycopg2 cursor.
    table_name : name of the table in database
    column_name : name of the column which will be turned into list

    Return: a list containing all elements of the column 
    """
    cur.execute(f'SELECT {column_name} FROM {table_name}')
    tuples = cur.fetchall()
    list_of_column = [id[0] for id in tuples]
    return list_of_column


def empty_check(conn, cursor , table_name):
    """Checks if the table is empty to verify before insertion
    
    Arguments
    conn : connection to the database
    cursor: An open psycopg2 cursor.
    table_name : name of the table in database
    
    Return : a boolean to show if it empty or not 
    """
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    if count == 0:
        return True
    else: 
        return False
        

def insertion(conn , cursor, table_name, insert_column, values, on_conflict = True,conflict_column=''):
    """insert a list of tuples into a database table
    
    Arguments
    conn : connection to the database
    cursor: An open psycopg2 cursor.
    table_name : name of the table in database
    insert_coumn: a string of columns to be inserted separated by a comma
    values : a list of values in tuples 
    on_conflict : optional flag to show on coflict columns in a schema 
    conflict_column : a string containing the conflict column/s for the schema      
    """
    if on_conflict:
        query = f"""INSERT INTO {table_name} ({insert_column}) VALUES %s
                    ON CONFLICT ({conflict_column}) DO NOTHING"""
    else:
        query = f"""INSERT INTO {table_name} ({insert_column}) VALUES %s"""
    # saving by batches 
    execute_values(cursor, query, values)


def key_id(cur,id_col,key_col,table_name,condition=''):
    """Builds a lookup dict mapping natural IDs to surrogate keys.

    Queries a dw schema dimension table and returns a dict for translating
    OLTP natural keys (e.g. product_id) into their corresponding dw
    surrogate keys (e.g. product_key), for use when populating fact tables.

    Args:
        cur: An open psycopg2 cursor.
        id_col: Name of the natural key column (becomes the dict's keys).
        key_col: Name of the surrogate key column (becomes the dict's values).
        table_name: Fully-qualified table to query, e.g. 'dw.dim_product'.
        condition: Optional SQL WHERE clause (e.g. 'WHERE is_current = TRUE'),
            used for SCD Type 2 tables to filter to only the current row
            per natural key. Defaults to no filter.

    Returns:
        A dict mapping each id_col value to its corresponding key_col value,
        e.g. {101: 55, 102: 56, ...}.
    """
    cur.execute(f'SELECT {id_col},{key_col} FROM {table_name} {condition}')
    id_key_tuples = cur.fetchall()
    dict_id_key = dict()

    for id, key in id_key_tuples:
        dict_id_key[id]=key
    

    return dict_id_key
    
    




