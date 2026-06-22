import sqlite3, os, random
from datetime import datetime, timedelta

DB_PATH = "data/business.db"
os.makedirs("data", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT    NOT NULL,
    email            TEXT,
    phone            TEXT,
    city             TEXT,
    country          TEXT,
    industry         TEXT,
    annual_revenue   REAL,
    employee_count   INTEGER,
    account_manager  TEXT,
    credit_score     INTEGER,
    status           TEXT,
    created_at       TEXT
);

CREATE TABLE products (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    category       TEXT,
    price          REAL,
    stock_quantity INTEGER,
    description    TEXT,
    unit           TEXT,
    discount_rate  REAL,
    tax_rate       REAL,
    supplier       TEXT,
    launch_date    TEXT,
    is_active      INTEGER
);

CREATE TABLE orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER,
    order_date      TEXT,
    status          TEXT,
    subtotal        REAL,
    discount_amount REAL,
    tax_amount      REAL,
    total_amount    REAL,
    payment_method  TEXT,
    sales_rep       TEXT,
    delivery_date   TEXT,
    notes           TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER,
    product_id      INTEGER,
    quantity        INTEGER,
    unit_price      REAL,
    discount_percent REAL,
    line_total      REAL,
    FOREIGN KEY (order_id)   REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE invoices (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id       INTEGER,
    invoice_number TEXT,
    invoice_date   TEXT,
    due_date       TEXT,
    subtotal       REAL,
    tax_amount     REAL,
    total_amount   REAL,
    paid_amount    REAL,
    payment_date   TEXT,
    status         TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
""")

industries = ["Auto Finance", "Leasing", "Banking", "Insurance", "Real Estate"]
managers   = ["Ahsan Raza", "Maria Qureshi", "Tariq Mehmood", "Sana Baig", "Faisal Awan"]
cities     = ["Lahore", "Karachi", "Islamabad", "Peshawar", "Multan",
              "Faisalabad", "Quetta", "Sialkot", "Gujranwala", "Rawalpindi"]

customers = [
    ("Ali Hassan",      "ali@gmail.com",     "0301-1111111", cities[0], "Pakistan", "Auto Finance",  5000000,  120, managers[0], 780, "active"),
    ("Sara Khan",       "sara@gmail.com",    "0302-2222222", cities[1], "Pakistan", "Leasing",       8000000,  200, managers[1], 820, "active"),
    ("Ahmed Malik",     "ahmed@gmail.com",   "0303-3333333", cities[2], "Pakistan", "Banking",      12000000,  350, managers[2], 760, "active"),
    ("Fatima Noor",     "fatima@gmail.com",  "0304-4444444", cities[3], "Pakistan", "Insurance",     3000000,   80, managers[3], 690, "active"),
    ("Usman Tariq",     "usman@gmail.com",   "0305-5555555", cities[4], "Pakistan", "Real Estate",  15000000,  500, managers[4], 850, "active"),
    ("Zara Sheikh",     "zara@gmail.com",    "0306-6666666", cities[5], "Pakistan", "Auto Finance",  4500000,  100, managers[0], 710, "inactive"),
    ("Bilal Chaudhry",  "bilal@gmail.com",   "0307-7777777", cities[6], "Pakistan", "Leasing",       6000000,  150, managers[1], 800, "active"),
    ("Hina Javed",      "hina@gmail.com",    "0308-8888888", cities[7], "Pakistan", "Banking",       9000000,  250, managers[2], 770, "active"),
    ("Kamran Iqbal",    "kamran@gmail.com",  "0309-9999999", cities[8], "Pakistan", "Insurance",     2500000,   60, managers[3], 650, "active"),
    ("Amna Riaz",       "amna@gmail.com",    "0310-0000000", cities[9], "Pakistan", "Real Estate",  18000000,  600, managers[4], 900, "active"),
    ("Hassan Abbasi",   "hassan@gmail.com",  "0311-1212121", cities[0], "Pakistan", "Auto Finance",  7000000,  180, managers[0], 790, "active"),
    ("Nadia Butt",      "nadia@gmail.com",   "0312-2323232", cities[1], "Pakistan", "Leasing",      11000000,  300, managers[1], 830, "active"),
    ("Imran Shah",      "imran@gmail.com",   "0313-3434343", cities[2], "Pakistan", "Banking",       5500000,  140, managers[2], 720, "inactive"),
    ("Sobia Malik",     "sobia@gmail.com",   "0314-4545454", cities[3], "Pakistan", "Insurance",     4000000,   90, managers[3], 740, "active"),
    ("Waqas Ahmed",     "waqas@gmail.com",   "0315-5656565", cities[4], "Pakistan", "Real Estate",  22000000,  700, managers[4], 880, "active"),
]
for c in customers:
    created = (datetime.now() - timedelta(days=random.randint(60, 500))).strftime("%Y-%m-%d")
    cur.execute("""INSERT INTO customers
        (name,email,phone,city,country,industry,annual_revenue,employee_count,
         account_manager,credit_score,status,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", (*c, created))

products = [
    ("Auto Finance A",    "Auto Finance", 150000, 50, "Basic auto financing",    "package", 5.0,  13.0, "NETSOL",    "2024-01-01", 1),
    ("Auto Finance B",    "Auto Finance", 250000, 30, "Premium auto financing",  "package", 3.0,  13.0, "NETSOL",    "2024-02-01", 1),
    ("Lease Standard",    "Leasing",      120000, 40, "Standard lease plan",     "plan",    4.0,  13.0, "NETSOL",    "2024-01-15", 1),
    ("Lease Premium",     "Leasing",      300000, 20, "Premium lease plan",      "plan",    2.0,  13.0, "NETSOL",    "2024-03-01", 1),
    ("Personal Loan S",   "Loans",         50000,100, "Small personal loan",     "loan",    6.0,  13.0, "FinBank",   "2023-06-01", 1),
    ("Personal Loan L",   "Loans",         80000, 80, "Large personal loan",     "loan",    5.0,  13.0, "FinBank",   "2023-06-01", 1),
    ("SME Package",       "SME",          500000, 15, "SME finance package",     "package", 2.5,  13.0, "BizFund",   "2024-04-01", 1),
    ("Housing Plan",      "Housing",      750000, 10, "Housing finance plan",    "plan",    1.5,  13.0, "HouseCo",   "2023-12-01", 1),
    ("Microfinance",      "Microfinance",  20000,200, "Small microfinance",      "loan",    7.0,  13.0, "MicroFund", "2024-01-01", 1),
    ("Business Premium",  "SME",          900000,  8, "Premium business loan",   "loan",    1.0,  13.0, "BizFund",   "2024-05-01", 1),
]
for p in products:
    cur.execute("""INSERT INTO products
        (name,category,price,stock_quantity,description,unit,
         discount_rate,tax_rate,supplier,launch_date,is_active)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", p)

payment_methods = ["Bank Transfer", "Cheque", "Online", "Cash"]
sales_reps      = ["Raza Ali", "Noman Khan", "Ayesha Siddiqui", "Zubair Hussain", "Mehwish Tariq"]
order_statuses  = ["completed","completed","completed","pending","cancelled"]

for i in range(1, 51):
    customer_id    = random.randint(1, 15)
    days_ago       = random.randint(1, 365)
    order_date     = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    delivery_date  = (datetime.now() - timedelta(days=days_ago - 7)).strftime("%Y-%m-%d")
    status         = random.choice(order_statuses)
    product_id     = random.randint(1, 10)
    quantity       = random.randint(1, 3)
    payment_method = random.choice(payment_methods)
    sales_rep      = random.choice(sales_reps)

    cur.execute("SELECT price, discount_rate, tax_rate FROM products WHERE id=?", (product_id,))
    price, disc_rate, tax_rate = cur.fetchone()

    subtotal    = round(price * quantity, 2)
    discount    = round(subtotal * disc_rate / 100, 2)
    tax         = round((subtotal - discount) * tax_rate / 100, 2)
    total       = round(subtotal - discount + tax, 2)

    cur.execute("""INSERT INTO orders
        (customer_id,order_date,status,subtotal,discount_amount,tax_amount,
         total_amount,payment_method,sales_rep,delivery_date,notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (customer_id, order_date, status, subtotal, discount, tax,
         total, payment_method, sales_rep, delivery_date, f"Order #{i}"))
    order_id = cur.lastrowid

    disc_pct   = disc_rate
    line_total = round((price - price * disc_pct / 100) * quantity, 2)
    cur.execute("""INSERT INTO order_items
        (order_id,product_id,quantity,unit_price,discount_percent,line_total)
        VALUES (?,?,?,?,?,?)""",
        (order_id, product_id, quantity, price, disc_pct, line_total))

    inv_number   = f"INV-2024-{order_id:04d}"
    invoice_date = order_date
    due_date     = (datetime.strptime(order_date, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
    inv_status   = "paid" if status == "completed" else ("unpaid" if status == "pending" else "cancelled")
    paid_amount  = total if inv_status == "paid" else 0.0
    payment_date = delivery_date if inv_status == "paid" else None

    cur.execute("""INSERT INTO invoices
        (order_id,invoice_number,invoice_date,due_date,subtotal,tax_amount,
         total_amount,paid_amount,payment_date,status)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (order_id, inv_number, invoice_date, due_date, subtotal, tax,
         total, paid_amount, payment_date, inv_status))

conn.commit()
conn.close()
print("✅ Database created:", DB_PATH)
print("15 customers | 10 products | 50 orders | 50 invoices")