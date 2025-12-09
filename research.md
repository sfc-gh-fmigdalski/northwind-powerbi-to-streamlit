# Northwind PowerBI to Streamlit Migration Research

## Overview
This document details the migration of the Northwind PowerBI dashboard to a Streamlit application backed by Snowflake.

## Database Suffix
All Snowflake databases will use suffix: **f90022**

## PowerBI Project Structure

### Pages (3 total)
1. **Dashboard (Overview)** - Main dashboard with KPIs, map, and charts
2. **Employees** - Employee performance analysis
3. **Category and Product** - Product and category analysis

### Data Model (from PowerBI)

#### Tables
1. **Order_Details** (Fact Table) - Denormalized with customer, employee, shipper data
   - Columns: OrderID, ProductID, UnitPrice, Quantity, Discount (%), OrderDate, ShippedDate, CompanyName, ContactName, ContactTitle, City, Country, LastName, Employee Name, Title, HireDate, City.1, Shipping Company
   - **Calculated Columns:**
     - Gross Revenue = UnitPrice * Quantity
     - Discount ($) = Gross Revenue * Discount (%)
     - Net Revenue = Gross Revenue - Discount ($)
     - Days to Ship = ShippedDate - OrderDate

2. **Product** (Dimension)
   - Columns: CategoryID, Category Name, Description, ProductID, Product Name, SupplierID, UnitPrice, UnitsInStock, UnitsOnOrder

3. **Suppliers** (Dimension)
   - Columns: SupplierID, CompanyName, ContactName, ContactTitle, City, Country

#### Measures (DAX)
- Orders = DISTINCTCOUNT(Order_Details[OrderID])
- Net Revenue per order = DIVIDE(SUM(Order_Details[Net Revenue]), Orders, BLANK())

#### Relationships
- Order_Details.ProductID -> Product.ProductID
- Product.SupplierID -> Suppliers.SupplierID
- Order_Details.OrderDate -> LocalDateTable.Date
- Order_Details.ShippedDate -> LocalDateTable.Date
- Order_Details.HireDate -> LocalDateTable.Date

## PostgreSQL Source Database

### Schema (northwind database)
| Table | Row Count | Description |
|-------|-----------|-------------|
| order_details | 2155 | Order line items |
| orders | 830 | Order headers |
| products | 77 | Product catalog |
| categories | 8 | Product categories |
| employees | 9 | Employee records |
| customers | 91 | Customer records |
| suppliers | 29 | Supplier records |
| shippers | 6 | Shipping companies |

### Key Columns for Migration

**order_details:**
- order_id, product_id, unit_price, quantity, discount

**orders:**
- order_id, customer_id, employee_id, order_date, shipped_date, ship_via

**products:**
- product_id, product_name, supplier_id, category_id, unit_price, units_in_stock, units_on_order

**categories:**
- category_id, category_name, description

**employees:**
- employee_id, last_name, first_name, title, hire_date, city

**customers:**
- customer_id, company_name, contact_name, contact_title, city, country

**shippers:**
- shipper_id, company_name

**suppliers:**
- supplier_id, company_name, contact_name, contact_title, city, country

## Snowflake Target Schema

### Database Structure
- Database: NORTHWIND_f90022
- Schema: PUBLIC

### Tables to Create
1. **ORDER_DETAILS_FACT** - Denormalized fact table matching PowerBI model
2. **PRODUCT_DIM** - Product dimension
3. **SUPPLIERS_DIM** - Suppliers dimension

### Views to Create (matching PowerBI transformations)
1. **V_ORDER_DETAILS** - Main view with calculated columns
2. **V_PRODUCT** - Product view with category info
3. **V_SUPPLIERS** - Suppliers view

## Dashboard Visuals

### Page 1: Dashboard (Overview)
| Visual Type | Title | Data Fields |
|-------------|-------|-------------|
| Slicer | Category Name, Product Name | Product[Category Name], Product[Product Name] |
| Slicer | Country, City | Order_Details[Country], Order_Details[City] |
| Slicer | Title, Employee Name | Order_Details[Title], Order_Details[Employee Name] |
| Date Slicer | Date Range | Order_Details[OrderDate] |
| Card | Sum of Gross Revenue | SUM(Gross Revenue) = 774.4K |
| Card | Sum of Discount ($) | SUM(Discount ($)) = 51.7K |
| Card | Sum of Net Revenue | SUM(Net Revenue) = 722.6K |
| Card | Orders | DISTINCTCOUNT(OrderID) = 474 |
| Card | Sum of Quantity | SUM(Quantity) = 30.3K |
| Gauge | Average Days to Ship | AVG(Days to Ship) = 8.39 |
| Map | Net Revenue by Country and City | Geo: Country, City; Value: Net Revenue |
| Combo Chart | Total Orders Vs Gross Revenue by Month | Orders + Gross Revenue by Month |
| Bar Chart | Average Days to ship by Shipping Company | AVG(Days to Ship) by Shipping Company |

### Page 2: Employees
| Visual Type | Title | Data Fields |
|-------------|-------|-------------|
| Bar Chart | Top 5 Employees by order | TOP 5 Employee Name by Orders |
| Bar Chart | Bottom 5 Employees by orders | BOTTOM 5 Employee Name by Orders |
| Table | Title and Employee level Performance | Title, Orders, Quantity, Gross Revenue, Discount ($), Net Revenue |
| Waterfall | Net Revenue by Employee Title | Net Revenue by Title with Increase/Decrease |
| Column Chart | Net Revenue per order by Employee | Net Revenue per order by Employee Name |

### Page 3: Category and Product
| Visual Type | Title | Data Fields |
|-------------|-------|-------------|
| Bar Chart | Top 5 Products by Orders | TOP 5 Product Name by Orders |
| Bar Chart | Bottom 5 Products by order | BOTTOM 5 Product Name by Orders |
| Table | Category and Product level Performance | Category Name, Orders, Quantity, Gross Revenue, Discount ($), Net Revenue |
| Matrix | Unit in Stock and Unit on Order | Category Name, UnitsInStock, UnitsOnOrder |
| Column Chart | Unit in Stock by Category and Product | UnitsInStock by Category Name |

## Migration Approach

### Phase 1: Data Migration
1. Extract data from PostgreSQL using SQL JOINs to denormalize
2. Apply PowerBI transformations (calculated columns) in SQL
3. Load to Snowflake tables/views

### Phase 2: Streamlit App
1. Create filters matching PowerBI slicers
2. Implement KPI cards with sparklines
3. Create charts using Plotly
4. Match layout to PowerBI screenshots

### Phase 3: Testing
1. Compare aggregate values
2. Screenshot comparison
3. Interactive testing of filters
