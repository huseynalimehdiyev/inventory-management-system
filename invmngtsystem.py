import sqlite3
import pandas as pd
import streamlit as st

DB_NAME = "inventory_gui.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Tables
    c.execute('''CREATE TABLE IF NOT EXISTS Categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS Products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT, 
                    category_id INTEGER, 
                    price REAL, 
                    stock_quantity INTEGER DEFAULT 0,
                    FOREIGN KEY(category_id) REFERENCES Categories(category_id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS Orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    customer_name TEXT, 
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS OrderDetails (
                    detail_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    order_id INTEGER, 
                    product_id INTEGER, 
                    quantity INTEGER, 
                    sold_price REAL,
                    FOREIGN KEY(order_id) REFERENCES Orders(order_id),
                    FOREIGN KEY(product_id) REFERENCES Products(product_id))''')

    c.execute('''CREATE TRIGGER IF NOT EXISTS DeductStock
                 AFTER INSERT ON OrderDetails
                 BEGIN
                    UPDATE Products SET stock_quantity = stock_quantity - NEW.quantity
                    WHERE product_id = NEW.product_id;
                 END;''')

    # Seed Data if empty
    c.execute("SELECT COUNT(*) FROM Categories")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO Categories (name) VALUES ('Electronics'), ('Home'), ('Clothing')")
        c.execute("INSERT INTO Products (name, category_id, price, stock_quantity) VALUES ('iPhone 14', 1, 999.0, 20)")
        c.execute(
            "INSERT INTO Products (name, category_id, price, stock_quantity) VALUES ('Coffee Maker', 2, 85.0, 15)")

    conn.commit()
    conn.close()



# Interface using Streamlit
st.set_page_config(page_title="Inventory Master", layout="wide")


init_db()

st.title("Inventory Management System")
st.markdown("Simple, effective warehouse management system")


menu = ["Stock", "Sell Product", "Add New Item", "Sales Report"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Stock":
    st.subheader("Current Inventory Status")

    # Load data using pandas
    conn = get_connection()
    df = pd.read_sql_query("SELECT product_id, name, price, stock_quantity FROM Products", conn)
    conn.close()

    st.dataframe(df, use_container_width=True)


    col1, col2 = st.columns(2)
    col1.metric("Total Products", len(df))
    col2.metric("Total Stock Value", f"${(df['price'] * df['stock_quantity']).sum():,.2f}")

elif choice == "Sell Product":
    st.subheader("🛒 Create New Order")

    conn = get_connection()
    products = pd.read_sql_query("SELECT product_id, name, price, stock_quantity FROM Products", conn)
    conn.close()


    with st.form("sell_form"):
        customer_name = st.text_input("Customer Name")

        # Create a dictionary for the dropdown: "Name (Price) - Stock left"
        product_options = {row['product_id']: f"{row['name']} (${row['price']}) - Stock: {row['stock_quantity']}"
                           for index, row in products.iterrows()}

        selected_id = st.selectbox("Select Product", options=list(product_options.keys()),
                                   format_func=lambda x: product_options[x])
        quantity = st.number_input("Quantity", min_value=1, value=1)

        submitted = st.form_submit_button("Confirm Sale")

        if submitted:
            conn = get_connection()
            c = conn.cursor()

            # Check stock
            c.execute("SELECT price, stock_quantity FROM Products WHERE product_id = ?", (selected_id,))
            res = c.fetchone()
            price, current_stock = res

            if current_stock >= quantity:
                #create order
                c.execute("INSERT INTO Orders (customer_name) VALUES (?)", (customer_name,))
                order_id = c.lastrowid

                # add details-Trigger will reduce stock automatical
                c.execute("INSERT INTO OrderDetails (order_id, product_id, quantity, sold_price) VALUES (?, ?, ?, ?)",
                          (order_id, selected_id, quantity, price))
                conn.commit()
                st.success(f"✅ Sold {quantity} items to {customer_name}! Stock updated.")
            else:
                st.error(f"❌ Not enough stock! Available: {current_stock}")
            conn.close()

elif choice == "Add New Item":
    st.subheader("➕ Add New Product to Database")

    with st.form("add_form"):
        name = st.text_input("Product Name")

        conn = get_connection()
        cats = pd.read_sql("SELECT category_id, name FROM Categories", conn)
        conn.close()

        cat_options = {row['category_id']: row['name'] for index, row in cats.iterrows()}
        cat_id = st.selectbox("Category", options=list(cat_options.keys()), format_func=lambda x: cat_options[x])

        price = st.number_input("Price ($)", min_value=0.0)
        stock = st.number_input("Initial Stock", min_value=1)

        if st.form_submit_button("Add Product"):
            conn = get_connection()
            conn.execute("INSERT INTO Products (name, category_id, price, stock_quantity) VALUES (?, ?, ?, ?)",
                         (name, cat_id, price, stock))
            conn.commit()
            conn.close()
            st.success(f"✅ {name} added to database!")

elif choice == "Sales Report":
    st.subheader("📈 Sales History")

    conn = get_connection()
    query = '''
        SELECT o.order_id, o.order_date, o.customer_name, p.name AS product, od.quantity, (od.quantity * od.sold_price) AS total_revenue
        FROM OrderDetails od
        JOIN Orders o ON od.order_id = o.order_id
        JOIN Products p ON od.product_id = p.product_id
        ORDER BY o.order_date DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()

    st.dataframe(df, use_container_width=True)
    st.bar_chart(df, x="product", y="total_revenue")