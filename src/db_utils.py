from psycopg2.extras import execute_values

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
