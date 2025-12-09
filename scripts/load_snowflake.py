#!/usr/bin/env python3
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

DB_SUFFIX = 'f90022'
DATABASE_NAME = f'NORTHWIND_{DB_SUFFIX}'
SCHEMA_NAME = 'PUBLIC'
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


def get_snowflake_connection():
    private_key_path = os.path.expanduser('~/.ssh/sv_pv_rsa_ket.p8')
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )
    
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    conn = snowflake.connector.connect(
        account='sfengineering-ai_powered_playground',
        user='SNOWVATION_AI_FIRST_SVC',
        private_key=private_key_bytes,
        role='unit_tester',
        warehouse='unit_tester_warehouse'
    )
    return conn


def setup_database(conn):
    cur = conn.cursor()
    
    cur.execute(f'CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}')
    cur.execute(f'USE DATABASE {DATABASE_NAME}')
    cur.execute(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}')
    cur.execute(f'USE SCHEMA {SCHEMA_NAME}')
    
    cur.close()
    print(f'Database {DATABASE_NAME} created')


def load_data(conn):
    cur = conn.cursor()
    cur.execute(f'USE DATABASE {DATABASE_NAME}')
    cur.execute(f'USE SCHEMA {SCHEMA_NAME}')
    
    # Load Order Details
    print('Loading ORDER_DETAILS_FACT...')
    df = pd.read_csv(os.path.join(DATA_DIR, 'order_details_fact.csv'))
    df.columns = ['ORDERID', 'PRODUCTID', 'UNITPRICE', 'QUANTITY', 'DISCOUNT_PCT', 
                  'ORDERDATE', 'SHIPPEDDATE', 'COMPANYNAME', 'CONTACTNAME', 'CONTACTTITLE',
                  'CITY', 'COUNTRY', 'LASTNAME', 'EMPLOYEENAME', 'TITLE', 'HIREDATE',
                  'EMPLOYEECITY', 'SHIPPINGCOMPANY', 'GROSSREVENUE', 'DISCOUNTAMOUNT', 
                  'NETREVENUE', 'DAYSTOSHIP']
    
    # Convert date columns
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE']).dt.date
    df['SHIPPEDDATE'] = pd.to_datetime(df['SHIPPEDDATE']).dt.date
    df['HIREDATE'] = pd.to_datetime(df['HIREDATE']).dt.date
    
    success, nchunks, nrows, _ = write_pandas(conn, df, 'ORDER_DETAILS_FACT', auto_create_table=True, overwrite=True)
    print(f'  Loaded {nrows} rows')
    
    # Load Product
    print('Loading PRODUCT_DIM...')
    df = pd.read_csv(os.path.join(DATA_DIR, 'product_dim.csv'))
    df.columns = ['CATEGORYID', 'CATEGORYNAME', 'DESCRIPTION', 'PRODUCTID', 'PRODUCTNAME',
                  'SUPPLIERID', 'UNITPRICE', 'UNITSINSTOCK', 'UNITSONORDER']
    success, nchunks, nrows, _ = write_pandas(conn, df, 'PRODUCT_DIM', auto_create_table=True, overwrite=True)
    print(f'  Loaded {nrows} rows')
    
    # Load Suppliers
    print('Loading SUPPLIERS_DIM...')
    df = pd.read_csv(os.path.join(DATA_DIR, 'suppliers_dim.csv'))
    df.columns = ['SUPPLIERID', 'COMPANYNAME', 'CONTACTNAME', 'CONTACTTITLE', 'CITY', 'COUNTRY']
    success, nchunks, nrows, _ = write_pandas(conn, df, 'SUPPLIERS_DIM', auto_create_table=True, overwrite=True)
    print(f'  Loaded {nrows} rows')
    
    cur.close()


def create_views(conn):
    cur = conn.cursor()
    cur.execute(f'USE DATABASE {DATABASE_NAME}')
    cur.execute(f'USE SCHEMA {SCHEMA_NAME}')
    
    cur.execute("""
    CREATE OR REPLACE VIEW V_ORDER_DETAILS AS
    SELECT 
        o.*,
        p.CATEGORYNAME,
        p.PRODUCTNAME,
        p.UNITSINSTOCK,
        p.UNITSONORDER
    FROM ORDER_DETAILS_FACT o
    LEFT JOIN PRODUCT_DIM p ON o.PRODUCTID = p.PRODUCTID
    """)
    
    cur.close()
    print('Views created')


def verify_data(conn):
    cur = conn.cursor()
    cur.execute(f'USE DATABASE {DATABASE_NAME}')
    cur.execute(f'USE SCHEMA {SCHEMA_NAME}')
    
    print()
    print('=== Data Verification ===')
    
    cur.execute('SELECT COUNT(DISTINCT ORDERID) FROM ORDER_DETAILS_FACT')
    orders = cur.fetchone()[0]
    print(f'Total Orders: {orders}')
    
    cur.execute('SELECT SUM(GROSSREVENUE) FROM ORDER_DETAILS_FACT')
    gross = cur.fetchone()[0]
    print(f'Total Gross Revenue: {gross:,.2f}')
    
    cur.execute('SELECT SUM(DISCOUNTAMOUNT) FROM ORDER_DETAILS_FACT')
    discount = cur.fetchone()[0]
    print(f'Total Discount ($): {discount:,.2f}')
    
    cur.execute('SELECT SUM(NETREVENUE) FROM ORDER_DETAILS_FACT')
    net = cur.fetchone()[0]
    print(f'Total Net Revenue: {net:,.2f}')
    
    cur.execute('SELECT SUM(QUANTITY) FROM ORDER_DETAILS_FACT')
    qty = cur.fetchone()[0]
    print(f'Total Quantity: {qty:,}')
    
    cur.execute('SELECT AVG(DAYSTOSHIP) FROM ORDER_DETAILS_FACT WHERE DAYSTOSHIP IS NOT NULL')
    avg_days = cur.fetchone()[0]
    print(f'Average Days to Ship: {avg_days:.2f}')
    
    cur.close()


def main():
    print('Connecting to Snowflake...')
    conn = get_snowflake_connection()
    
    setup_database(conn)
    load_data(conn)
    create_views(conn)
    verify_data(conn)
    
    conn.close()
    print()
    print('Data migration to Snowflake complete!')


if __name__ == '__main__':
    main()
