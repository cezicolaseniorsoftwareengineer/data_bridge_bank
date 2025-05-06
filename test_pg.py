# -*- coding: utf-8 -*-
import psycopg2

print("Testing PostgreSQL connection...")

try:
    conn = psycopg2.connect(
        host="localhost",
        database="DataBridge", 
        user="postgres",
        password="640064"
    )
    print("SUCCESS: Connected to PostgreSQL!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print(f"PostgreSQL version: {cursor.fetchone()[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")