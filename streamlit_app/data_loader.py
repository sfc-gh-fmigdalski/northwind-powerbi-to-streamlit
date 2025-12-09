import streamlit as st
import snowflake.connector
import pandas as pd
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import os

DB_SUFFIX = 'f90022'
DATABASE_NAME = f'NORTHWIND_{DB_SUFFIX}'
SCHEMA_NAME = 'PUBLIC'


@st.cache_resource
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
        warehouse='unit_tester_warehouse',
        database=DATABASE_NAME,
        schema=SCHEMA_NAME
    )
    return conn


@st.cache_data(ttl=600)
def load_order_details():
    conn = get_snowflake_connection()
    query = """
    SELECT * FROM V_ORDER_DETAILS
    """
    df = pd.read_sql(query, conn)
    df.columns = [c.lower() for c in df.columns]
    return df


@st.cache_data(ttl=600)
def load_products():
    conn = get_snowflake_connection()
    query = "SELECT * FROM PRODUCT_DIM"
    df = pd.read_sql(query, conn)
    df.columns = [c.lower() for c in df.columns]
    return df


@st.cache_data(ttl=600)
def load_suppliers():
    conn = get_snowflake_connection()
    query = "SELECT * FROM SUPPLIERS_DIM"
    df = pd.read_sql(query, conn)
    df.columns = [c.lower() for c in df.columns]
    return df
