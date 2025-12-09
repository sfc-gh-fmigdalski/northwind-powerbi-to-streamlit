#!/usr/bin/env python3
import psycopg2

def analyze_database():
    conn = psycopg2.connect(
        host="localhost",
        port=55432,
        user="postgres",
        password="postgres",
        database="northwind"
    )
    cur = conn.cursor()

    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;")
    tables = [row[0] for row in cur.fetchall()]

    print('Tables in northwind database:')
    for t in tables:
        cur.execute('SELECT COUNT(*) FROM ' + t)
        count = cur.fetchone()[0]
        print('  - ' + t + ': ' + str(count) + ' rows')

    print()
    print('=' * 60)
    print('Table Schemas:')
    print('=' * 60)

    for table in tables:
        print()
        print(table + ':')
        cur.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '" + table + "' ORDER BY ordinal_position;")
        for col in cur.fetchall():
            nullable = '(nullable)' if col[2] == 'YES' else ''
            print('    ' + col[0] + ': ' + col[1] + ' ' + nullable)

    conn.close()

if __name__ == '__main__':
    analyze_database()
