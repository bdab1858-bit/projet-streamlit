import psycopg2

def get_connection():
    return psycopg2.connect(
        host="dpg-d5lsqtumcj7s73bm6k1g-a",
        database="edt_universitaire",
        user="admin",
        password="8ne6EUYzDjKXxv3d9axZElqbrV7w0skv",
        port="5432"
    )