#!/usr/bin/env python3
import psycopg2
import pandas as pd
import os

DB_CONFIG = {
    'host': 'localhost',
    'port': 55432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'northwind'
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


def extract_order_details_fact():
    query = '''
    SELECT 
        od.order_id as "OrderID",
        od.product_id as "ProductID",
        od.unit_price as "UnitPrice",
        od.quantity as "Quantity",
        od.discount as "Discount (%)",
        o.order_date as "OrderDate",
        o.shipped_date as "ShippedDate",
        c.company_name as "CompanyName",
        c.contact_name as "ContactName",
        c.contact_title as "ContactTitle",
        c.city as "City",
        c.country as "Country",
        e.last_name as "LastName",
        e.first_name as "Employee Name",
        e.title as "Title",
        e.hire_date as "HireDate",
        e.city as "City.1",
        sh.company_name as "Shipping Company",
        (od.unit_price * od.quantity) as "Gross Revenue",
        (od.unit_price * od.quantity * od.discount) as "Discount ($)",
        (od.unit_price * od.quantity) - (od.unit_price * od.quantity * od.discount) as "Net Revenue",
        CASE 
            WHEN o.shipped_date IS NOT NULL AND o.order_date IS NOT NULL 
            THEN (o.shipped_date - o.order_date)
            ELSE NULL 
        END as "Days to Ship"
    FROM order_details od
    JOIN orders o ON od.order_id = o.order_id
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN employees e ON o.employee_id = e.employee_id
    LEFT JOIN shippers sh ON o.ship_via = sh.shipper_id
    ORDER BY od.order_id, od.product_id
    '''
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def extract_product_dim():
    query = '''
    SELECT 
        c.category_id as "CategoryID",
        c.category_name as "Category Name",
        c.description as "Description",
        p.product_id as "ProductID",
        p.product_name as "Product Name",
        p.supplier_id as "SupplierID",
        p.unit_price as "UnitPrice",
        p.units_in_stock as "UnitsInStock",
        p.units_on_order as "UnitsOnOrder"
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    ORDER BY p.product_id
    '''
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def extract_suppliers_dim():
    query = '''
    SELECT 
        supplier_id as "SupplierID",
        company_name as "CompanyName",
        contact_name as "ContactName",
        contact_title as "ContactTitle",
        city as "City",
        country as "Country"
    FROM suppliers
    ORDER BY supplier_id
    '''
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print('Extracting Order_Details fact table...')
    order_details = extract_order_details_fact()
    order_details.to_csv(os.path.join(OUTPUT_DIR, 'order_details_fact.csv'), index=False)
    print(f'  Exported {len(order_details)} rows')
    
    print('Extracting Product dimension...')
    product = extract_product_dim()
    product.to_csv(os.path.join(OUTPUT_DIR, 'product_dim.csv'), index=False)
    print(f'  Exported {len(product)} rows')
    
    print('Extracting Suppliers dimension...')
    suppliers = extract_suppliers_dim()
    suppliers.to_csv(os.path.join(OUTPUT_DIR, 'suppliers_dim.csv'), index=False)
    print(f'  Exported {len(suppliers)} rows')
    
    print('Data extraction complete!')
    
    print()
    print('=== Summary Statistics ===')
    print(f'Total Orders: {order_details["OrderID"].nunique()}')
    print(f'Total Gross Revenue: {order_details["Gross Revenue"].sum():,.2f}')
    print(f'Total Discount ($): {order_details["Discount ($)"].sum():,.2f}')
    print(f'Total Net Revenue: {order_details["Net Revenue"].sum():,.2f}')
    print(f'Total Quantity: {order_details["Quantity"].sum():,}')
    avg_days = order_details["Days to Ship"].mean()
    print(f'Average Days to Ship: {avg_days:.2f}')


if __name__ == '__main__':
    main()
