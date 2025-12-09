import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from data_loader import load_order_details, load_products

st.set_page_config(
    page_title="Northwind Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match PowerBI styling
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: white; padding: 15px; border-radius: 5px; }
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; color: #1a365d; }
    .sidebar .sidebar-content { background-color: #1a365d; }
    h1, h2, h3 { color: #1a365d; }
    .plot-container { background-color: white; border-radius: 5px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# Load data
df = load_order_details()
products = load_products()

# Convert dates
df['orderdate'] = pd.to_datetime(df['orderdate'])
df['shippeddate'] = pd.to_datetime(df['shippeddate'])

# Sidebar navigation
st.sidebar.markdown("""
<div style="background-color: #1a365d; padding: 20px; color: white; margin: -1rem -1rem 1rem -1rem;">
    <h2 style="color: white; margin: 0;">Northwind</h2>
    <h3 style="color: white; margin: 0;">Dashboard</h3>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "",
    ["Overview", "Category and Product", "Employees"],
    label_visibility="collapsed"
)

# Filters
st.sidebar.markdown("### Filters")

# Category and Product filter
categories = sorted(df['categoryname'].dropna().unique())
selected_category = st.sidebar.selectbox("Category Name, Product Name", ["All"] + categories)

# Country, City filter
countries = sorted(df['country'].dropna().unique())
selected_country = st.sidebar.selectbox("Country, City", ["All"] + list(countries))

# Title, Employee Name filter
titles = sorted(df['title'].dropna().unique())
selected_title = st.sidebar.selectbox("Title, Employee Name", ["All"] + list(titles))

# Date range filter
min_date = df['orderdate'].min().date()
max_date = df['orderdate'].max().date()
# Default to match PowerBI screenshot (1996-11-10 to 1997-12-27)
default_start = date(1996, 11, 10)
default_end = date(1997, 12, 27)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(default_start, default_end),
    min_value=min_date,
    max_value=max_date
)

# Apply filters
filtered_df = df.copy()

if selected_category != "All":
    filtered_df = filtered_df[filtered_df['categoryname'] == selected_category]

if selected_country != "All":
    filtered_df = filtered_df[filtered_df['country'] == selected_country]

if selected_title != "All":
    filtered_df = filtered_df[filtered_df['title'] == selected_title]

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['orderdate'].dt.date >= start_date) &
        (filtered_df['orderdate'].dt.date <= end_date)
    ]


def format_number(num):
    if num >= 1000:
        return f"{num/1000:.1f}K"
    return f"{num:.0f}"


if page == "Overview":
    st.markdown("<h1 style=margin-bottom:0>Overview Dashboard</h1>", unsafe_allow_html=True)
    
    # KPI Cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    gross_rev = filtered_df['grossrevenue'].sum()
    discount = filtered_df['discountamount'].sum()
    net_rev = filtered_df['netrevenue'].sum()
    orders = filtered_df['orderid'].nunique()
    quantity = filtered_df['quantity'].sum()
    avg_days = filtered_df['daystoship'].mean()
    
    with col1:
        st.metric("Sum of Gross Revenue", format_number(gross_rev))
    with col2:
        st.metric("Sum of Discount ($)", format_number(discount))
    with col3:
        st.metric("Sum of Net Revenue", format_number(net_rev))
    with col4:
        st.metric("Orders", f"{orders:,}")
    with col5:
        st.metric("Sum of Quantity", format_number(quantity))
    with col6:
        st.metric("Avg Days to Ship", f"{avg_days:.2f}")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Net Revenue by Country and City")
        geo_data = filtered_df.groupby(['country', 'city'])['netrevenue'].sum().reset_index()
        fig = px.scatter_geo(
            geo_data,
            locations="country",
            locationmode="country names",
            size="netrevenue",
            hover_name="city",
            color_discrete_sequence=['#4a90d9'],
            projection="natural earth"
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            geo=dict(showframe=False, showcoastlines=True)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Total Orders Vs Gross Revenue by Month")
        monthly = filtered_df.groupby(filtered_df['orderdate'].dt.to_period('M')).agg({
            'orderid': 'nunique',
            'grossrevenue': 'sum'
        }).reset_index()
        monthly['orderdate'] = monthly['orderdate'].astype(str)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly['orderdate'], y=monthly['grossrevenue'], 
                            name='Gross Revenue', marker_color='#4a90d9'))
        fig.add_trace(go.Scatter(x=monthly['orderdate'], y=monthly['orderid'], 
                                name='Orders', yaxis='y2', mode='lines+markers',
                                line=dict(color='#1a365d')))
        fig.update_layout(
            yaxis=dict(title='Gross Revenue'),
            yaxis2=dict(title='Orders', overlaying='y', side='right'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Bottom chart
    st.markdown("### Average Days to Ship by Shipping Company")
    shipping = filtered_df.groupby('shippingcompany')['daystoship'].mean().sort_values(ascending=True).reset_index()
    fig = px.bar(shipping, y='shippingcompany', x='daystoship', orientation='h',
                color_discrete_sequence=['#4a90d9'],
                text='daystoship')
    fig.update_traces(texttemplate='%{text:.2f}', textposition='inside')
    fig.update_layout(
        xaxis_title='Average Days to Ship',
        yaxis_title='',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)


elif page == "Category and Product":
    st.markdown("<h1>Category and Product Analysis</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top/Bottom 5 Products by Orders")
        product_orders = filtered_df.groupby('productname')['orderid'].nunique().reset_index()
        product_orders.columns = ['Product', 'Orders']
        
        top5 = product_orders.nlargest(5, 'Orders')
        fig = px.bar(top5, y='Product', x='Orders', orientation='h',
                    color_discrete_sequence=['#4caf50'], title='Top 5 Products')
        fig.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig, use_container_width=True)
        
        bottom5 = product_orders.nsmallest(5, 'Orders')
        fig = px.bar(bottom5, y='Product', x='Orders', orientation='h',
                    color_discrete_sequence=['#ff7043'], title='Bottom 5 Products')
        fig.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Category and Product level Performance")
        cat_perf = filtered_df.groupby('categoryname').agg({
            'orderid': 'nunique',
            'quantity': 'sum',
            'grossrevenue': 'sum',
            'discountamount': 'sum',
            'netrevenue': 'sum'
        }).reset_index()
        cat_perf.columns = ['Category Name', 'Orders', 'Quantity', 'Gross Revenue', 'Discount ($)', 'Net Revenue']
        st.dataframe(cat_perf, use_container_width=True, hide_index=True)
        
        st.markdown("### Unit in Stock and Unit on Order")
        stock = products.groupby('categoryname').agg({
            'unitsinstock': 'sum',
            'unitsonorder': 'sum'
        }).reset_index()
        stock.columns = ['Category Name', 'Units In Stock', 'Units On Order']
        st.dataframe(stock, use_container_width=True, hide_index=True)
    
    st.markdown("### Units in Stock by Category")
    fig = px.bar(stock, x='Category Name', y='Units In Stock',
                color_discrete_sequence=['#4a90d9'],
                text='Units In Stock')
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)


elif page == "Employees":
    st.markdown("<h1>Employee Analysis</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top/Bottom 5 Employees by Orders")
        emp_orders = filtered_df.groupby('employeename')['orderid'].nunique().reset_index()
        emp_orders.columns = ['Employee', 'Orders']
        
        top5 = emp_orders.nlargest(5, 'Orders')
        fig = px.bar(top5, y='Employee', x='Orders', orientation='h',
                    color_discrete_sequence=['#4caf50'], title='Top 5 Employees')
        fig.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig, use_container_width=True)
        
        bottom5 = emp_orders.nsmallest(5, 'Orders')
        fig = px.bar(bottom5, y='Employee', x='Orders', orientation='h',
                    color_discrete_sequence=['#ff7043'], title='Bottom 5 Employees')
        fig.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Title and Employee level Performance")
        title_perf = filtered_df.groupby('title').agg({
            'orderid': 'nunique',
            'quantity': 'sum',
            'grossrevenue': 'sum',
            'discountamount': 'sum',
            'netrevenue': 'sum'
        }).reset_index()
        title_perf.columns = ['Title', 'Orders', 'Quantity', 'Gross Revenue', 'Discount ($)', 'Net Revenue']
        st.dataframe(title_perf, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Net Revenue by Employee Title")
        fig = px.bar(title_perf, x='Title', y='Net Revenue',
                    color_discrete_sequence=['#4a90d9'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Net Revenue per Order by Employee")
        emp_rev = filtered_df.groupby('employeename').agg({
            'netrevenue': 'sum',
            'orderid': 'nunique'
        }).reset_index()
        emp_rev['rev_per_order'] = emp_rev['netrevenue'] / emp_rev['orderid']
        emp_rev = emp_rev.sort_values('rev_per_order', ascending=False)
        
        fig = px.bar(emp_rev, x='employeename', y='rev_per_order',
                    color_discrete_sequence=['#4a90d9'],
                    text=emp_rev['rev_per_order'].round(0).astype(int))
        fig.update_traces(textposition='outside')
        fig.update_layout(xaxis_title='Employee Name', yaxis_title='Net Revenue per Order')
        st.plotly_chart(fig, use_container_width=True)
