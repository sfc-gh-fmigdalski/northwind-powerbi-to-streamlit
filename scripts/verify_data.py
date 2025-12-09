
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import os

# Connect to Snowflake
private_key_path = os.path.expanduser("~/.ssh/sv_pv_rsa_ket.p8")
with open(private_key_path, "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(), password=None, backend=default_backend()
    )

private_key_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

conn = snowflake.connector.connect(
    account="sfengineering-ai_powered_playground",
    user="SNOWVATION_AI_FIRST_SVC",
    private_key=private_key_bytes,
    role="unit_tester",
    warehouse="unit_tester_warehouse",
    database="NORTHWIND_f90022",
    schema="PUBLIC"
)

cur = conn.cursor()

# Apply the same date filter as PowerBI dashboard (1996-11-10 to 1997-12-27)
print("=" * 60)
print("Verification with PowerBI date filter (1996-11-10 to 1997-12-27)")
print("=" * 60)

# Gross Revenue
cur.execute("""
SELECT SUM(GROSSREVENUE) 
FROM ORDER_DETAILS_FACT 
WHERE ORDERDATE >= '1996-11-10' AND ORDERDATE <= '1997-12-27'
""")
gross = cur.fetchone()[0]
print(f"Gross Revenue: {gross:,.2f} (PowerBI: 774.4K = 774,400)")

# Discount
cur.execute("""
SELECT SUM(DISCOUNTAMOUNT) 
FROM ORDER_DETAILS_FACT 
WHERE ORDERDATE >= '1996-11-10' AND ORDERDATE <= '1997-12-27'
""")
discount = cur.fetchone()[0]
print(f"Discount ($): {discount:,.2f} (PowerBI: 51.7K = 51,700)")

# Net Revenue
cur.execute("""
SELECT SUM(NETREVENUE) 
FROM ORDER_DETAILS_FACT 
WHERE ORDERDATE >= '1996-11-10' AND ORDERDATE <= '1997-12-27'
""")
net = cur.fetchone()[0]
print(f"Net Revenue: {net:,.2f} (PowerBI: 722.6K = 722,600)")

# Orders (distinct count)
cur.execute("""
SELECT COUNT(DISTINCT ORDERID) 
FROM ORDER_DETAILS_FACT 
WHERE ORDERDATE >= '1996-11-10' AND ORDERDATE <= '1997-12-27'
""")
orders = cur.fetchone()[0]
print(f"Orders: {orders} (PowerBI: 474)")

# Quantity
cur.execute("""
SELECT SUM(QUANTITY) 
FROM ORDER_DETAILS_FACT 
WHERE ORDERDATE >= '1996-11-10' AND ORDERDATE <= '1997-12-27'
""")
qty = cur.fetchone()[0]
print(f"Quantity: {qty:,} (PowerBI: 30.3K = 30,300)")

# Average Days to Ship
cur.execute("""
SELECT AVG(DAYSTOSHIP) 
FROM ORDER_DETAILS_FACT 
WHERE ORDERDATE >= '1996-11-10' AND ORDERDATE <= '1997-12-27' 
AND DAYSTOSHIP IS NOT NULL
""")
avg_days = cur.fetchone()[0]
print(f"Avg Days to Ship: {avg_days:.2f} (PowerBI: 8.39)")

conn.close()
