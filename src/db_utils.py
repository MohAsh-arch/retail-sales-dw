from psycopg2.extras import execute_values
import psycopg2
import os 
from dotenv import load_dotenv

def db_connect():
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
    cur.execute(f'SELECT {column_name} FROM {table_name}')
    tuples = cur.fetchall()
    list_of_column = [id[0] for id in tuples]
    return list_of_column


def empty_check(conn, cursor , table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    if count == 0:
        return True
    else: 
        return False
        

def insertion(conn , cursor, table_name, insert_column, values, on_conflict = True,conflict_column=''):
    if on_conflict:
        query = f"""INSERT INTO {table_name} ({insert_column}) VALUES %s
                    ON CONFLICT ({conflict_column}) DO NOTHING"""
    else:
        query = f"""INSERT INTO {table_name} ({insert_column}) VALUES %s"""
    # saving by batches 
    execute_values(cursor, query, values)


def key_id(cur,id_col,key_col,table_name,condition=''):
    cur.execute(f'SELECT {id_col},{key_col} FROM {table_name} {condition}')
    id_key_tuples = cur.fetchall()
    dict_id_key = dict()

    for id, key in id_key_tuples:
        dict_id_key[id]=key
    

    return dict_id_key
    
    




