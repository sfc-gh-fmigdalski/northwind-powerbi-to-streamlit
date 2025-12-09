# Northwind PowerBI to Streamlit Migration

This project migrates the Northwind PowerBI dashboard to a Streamlit application backed by Snowflake.

## Project Structure

- scripts/ - Migration scripts
  - analyze_postgres.py - Analyze PostgreSQL database schema
  - extract_postgres.py - Extract data from PostgreSQL and transform for PowerBI model
  - load_snowflake.py - Load data into Snowflake
- streamlit_app/ - Streamlit application
  - app.py - Main dashboard application
  - data_loader.py - Snowflake data loading utilities
- data/ - Extracted CSV files (generated)
- research.md - Detailed research documentation

## Database Configuration

### PostgreSQL Source
- Host: localhost
- Port: 55432
- Database: northwind
- User: postgres
- Password: postgres

### Snowflake Target
- Database: NORTHWIND_f90022
- Schema: PUBLIC

## Setup Instructions

1. Install Dependencies: cd northwind-powerbi-to-streamlit && uv sync
2. Extract Data from PostgreSQL: uv run python scripts/extract_postgres.py
3. Load Data to Snowflake: uv run python scripts/load_snowflake.py
4. Run Streamlit App: uv run streamlit run streamlit_app/app.py

## Data Transformations

### Calculated Columns (in ORDER_DETAILS_FACT)
- Gross Revenue = UnitPrice * Quantity
- Discount ($) = Gross Revenue * Discount (%)
- Net Revenue = Gross Revenue - Discount ($)
- Days to Ship = ShippedDate - OrderDate

### Measures (calculated in app)
- Orders = DISTINCTCOUNT(OrderID)
- Net Revenue per order = SUM(Net Revenue) / Orders

## Dashboard Pages

1. Overview Dashboard - KPIs, Map, Charts
2. Category and Product - Product analysis
3. Employees - Employee performance

## Verification

Default filter (matching PowerBI screenshot): 1996-11-10 to 1997-12-27

Expected values with default filter:
- Gross Revenue: ~774.4K
- Discount ($): ~51.7K
- Net Revenue: ~722.6K
- Orders: 474
- Quantity: ~30.3K
- Avg Days to Ship: ~8.39
