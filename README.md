# 📦 Inventory & Sales Management System

![Python](https://img.shields.io/badge/Python-3%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![Status](https://img.shields.io/badge/Status-Completed-success)

## Overview

This project is a **Full-Stack Inventory Management System** built to simulate real-world warehouse operations. It bridges the gap between a robust **Relational Database (SQL)** and a modern, user-friendly **Frontend (Streamlit)**.

The system is designed to handle stock tracking, order processing, and sales analytics. Unlike simple CRUD applications, this project leverages **Database Triggers** to handle business logic (like stock reduction) automatically at the database level, ensuring data integrity and zero-latency updates.

---

## 🚀 Key Features

### 1.Interactive Dashboard
- Real-time visualization of current stock levels.
- Calculation of total inventory value using Pandas.
- Sortable and filterable data grids (Excel-like view).

### 2.Automated Stock Management (SQL Triggers)
- **Smart Logic:** When a sale is confirmed, the system automatically deducts the quantity from the `Products` table.
- **Why this matters:** This removes the need for extra Python calculations and prevents race conditions, handling logic directly within the DB engine.

### 3.Sales & Order Processing
- User-friendly form to select products, customers, and quantities.
- Validates stock availability before processing a transaction (prevents overselling).

### 4.Analytics & Reporting
- Detailed sales history generated using complex **SQL JOINs** (connecting Orders, Customers, and Product tables).
- Visual bar charts to analyze revenue per product.

---

## Technical Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.x | Core application logic. |
| **Frontend** | Streamlit | Web framework for data apps (No HTML/CSS required). |
| **Database** | SQLite | Serverless, relational database engine. |
| **Data Processing** | Pandas | Used for rendering tables and calculating metrics. |

---

## 🧠 Database Architecture

The database is normalized to **3rd Normal Form (3NF)** to ensure data consistency.

### Schema Structure
*   **`Categories`**: Stores product types.
*   **`Products`**: Stores item details and current stock (`One-to-Many` with Categories).
*   **`Orders`**: Stores customer info and timestamps.
*   **`OrderDetails`**: Stores specific items per order (`Many-to-Many` resolution).

### The "Magic" Code (Trigger)
This is the SQL trigger responsible for automating inventory updates:

```sql
CREATE TRIGGER DeductStock
AFTER INSERT ON OrderDetails
BEGIN
    UPDATE Products 
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
END;
```

## 🚀 **Running the App**

Setting up and launching the **Inventory & Sales Management System** is quick and simple. Just follow the steps below.

---

### **1️⃣ Install Dependencies**

Ensure you have **Python 3.9+** installed. Then install the required libraries:

```bash
pip install streamlit pandas
```

> **Note:** `sqlite3` comes built-in with Python — no installation needed.

---

### **2️⃣ Start the Application**

Open your terminal, navigate to your project folder, and run:

```bash
streamlit run app.py
```

This will launch the Streamlit development server.

---

### **3️⃣ Access the Web Interface**

After running the command, open your browser and go to:

```
http://localhost:8501
```

You now have access to the full **Inventory & Sales Management Dashboard**, including:

- 📦 Live Stock Overview  
- 🛒 Order Processing  
- 📊 Sales Analytics  
- 🔄 Automated Inventory Updates (Trigger-Based)

---
