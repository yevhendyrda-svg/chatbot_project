"""
Script to create a sample SQLite database with customers and orders.
Run once: python data/create_sample_db.py
"""
import sqlite3
import os
from datetime import datetime, timedelta

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

db_path = "data/sample.db"

# Remove old DB if it exists
if os.path.exists(db_path):
    os.remove(db_path)

# Connect and create schema
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create customers table
cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        country TEXT NOT NULL,
        signup_date TEXT NOT NULL
    )
""")

# Create orders table
cursor.execute("""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        order_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
""")

# Sample customers
customers = [
    ("Alice Johnson", "alice@example.com", "USA", "2023-01-15"),
    ("Bob Smith", "bob@example.com", "UK", "2023-02-20"),
    ("Charlie Brown", "charlie@example.com", "Germany", "2023-03-10"),
    ("Diana Prince", "diana@example.com", "France", "2023-04-05"),
    ("Eve Wilson", "eve@example.com", "USA", "2023-05-12"),
    ("Frank Miller", "frank@example.com", "Germany", "2023-06-18"),
    ("Grace Lee", "grace@example.com", "UK", "2023-07-22"),
    ("Henry Davis", "henry@example.com", "USA", "2023-08-30"),
    ("Iris Chen", "iris@example.com", "Canada", "2023-09-14"),
    ("Jack Norton", "jack@example.com", "USA", "2023-10-25"),
]

cursor.executemany("INSERT INTO customers (name, email, country, signup_date) VALUES (?, ?, ?, ?)", customers)

# Sample orders (customer_id, amount, order_date, status)
orders = [
    (1, 150.00, "2024-01-05", "completed"),
    (1, 200.50, "2024-02-10", "completed"),
    (2, 75.25, "2024-01-20", "completed"),
    (2, 120.00, "2024-03-15", "completed"),
    (2, 95.50, "2024-03-20", "pending"),
    (3, 310.00, "2024-02-01", "completed"),
    (4, 420.75, "2024-01-25", "completed"),
    (4, 180.00, "2024-03-05", "completed"),
    (5, 250.00, "2024-02-14", "completed"),
    (6, 340.25, "2024-01-30", "completed"),
    (7, 180.50, "2024-02-28", "completed"),
    (8, 520.00, "2024-03-01", "completed"),
    (8, 150.00, "2024-03-18", "pending"),
    (9, 275.75, "2024-02-20", "completed"),
    (10, 410.00, "2024-01-10", "completed"),
    (10, 95.50, "2024-02-22", "completed"),
    (10, 220.00, "2024-03-10", "pending"),
]

cursor.executemany("INSERT INTO orders (customer_id, amount, order_date, status) VALUES (?, ?, ?, ?)", orders)

conn.commit()
conn.close()

print(f"✓ Sample database created at {db_path}")
print(f"  - 10 customers")
print(f"  - 17 orders")
print(f"\nSchema:")
print(f"  customers: id, name, email, country, signup_date")
print(f"  orders: id, customer_id, amount, order_date, status")
