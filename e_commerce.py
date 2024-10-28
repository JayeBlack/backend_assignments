import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Creating the Customers Table
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS Customers(
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )'''
)

# Creating the Orders Table
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS Orders(
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        price REAL,
        quantity INTEGER,
        FOREIGN KEY(customer_id) REFERENCES Customers(customer_id),
        FOREIGN KEY(product_id) REFERENCES Products(product_id)
    )
    '''
)

# Creating the Products Table
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS Products(
        product_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL
    )
    '''
)

# Populate the Products Table with sample Ghanaian data
products = [
    (1, 'Jollof Rice', 30.0, 200),
    (2, 'Banku', 10.0, 150),
    (3, 'Gari Fortor', 15.0, 100),
    (4, 'Tilapia', 25.0, 80),
    (5, 'Kelewele', 5.0, 120),
    (6, 'Waakye', 12.0, 90),
    (7, 'Chicken Light Soup', 20.0, 70),
    (8, 'Beef Kebab', 18.0, 60),
]

cursor.executemany('INSERT OR IGNORE INTO Products (product_id, name, price, stock) VALUES (?, ?, ?, ?)', products)

# Populate the Customers Table with realistic email addresses
customers = [
    ('Kwame Nkrumah', 'kwame.nkrumah@gmail.com'),
    ('Akosua Agyapadie', 'akosua.agyapadie@gmail.com'),
    ('Kofi Annan', 'kofi.annan@gmail.com'),
    ('Abena Akufo-Addo', 'abena.akufoaddo@gmail.com'),
    ('Kwabena Boateng', 'kwabena.boateng@gmail.com'),
    ('Ama Serwah', 'ama.serwah@gmail.com'),
    ('Yaw Osei', 'yaw.osei@gmail.com'),
    ('Akua Afriyie', 'akua.afriyie@gmail.com'),
]

cursor.executemany('INSERT OR IGNORE INTO Customers (name, email) VALUES (?, ?)', customers)

# Commit the changes to ensure tables are populated
conn.commit()

# Decorator to validate user input
def validate_user_input(func):
    def wrapper(conn, cursor, customer_id, product_id, quantity):
        cursor.execute("SELECT stock FROM Products WHERE product_id=?", (product_id,))
        result = cursor.fetchone()
        if result and result[0] >= quantity:
            return func(conn, cursor, customer_id, product_id, quantity)
        else:
            print("Product not found or out of stock.")
    return wrapper

# Lambda for discounts (10%)
discount = lambda total_items: 0.10 if total_items > 10 else 0

@validate_user_input
def place_order(conn, cursor, customer_id, product_id, quantity):
    cursor.execute("SELECT price FROM Products WHERE product_id=?", (product_id,))
    product_data = cursor.fetchone()

    if product_data is None:
        print(f"Error: Product with ID '{product_id}' not found.")
        return

    price_per_item = product_data[0]
    total_price = price_per_item * quantity
    discount_percentage = discount(quantity)
    discount_amount = total_price * discount_percentage
    final_price = total_price - discount_amount

    cursor.execute('''INSERT INTO Orders (customer_id, product_id, price, quantity) 
                      VALUES (?, ?, ?, ?)''',
                   (customer_id, product_id, final_price, quantity))
    conn.commit()

    print(f"Order placed for {quantity} unit(s) of product ID {product_id}. Total Price: GHS {final_price:.2f}")

# Generator to stream order history for each customer
def get_order_history(conn, cursor, customer_id):
    cursor.execute("SELECT * FROM Orders WHERE customer_id=?", (customer_id,))
    while True:
        order = cursor.fetchone()
        if order is None:
            break
        yield order

# List Comprehension to summarize orders
def get_detailed_order_summary(conn, cursor, customer_id):
    cursor.execute('''
        SELECT Products.name AS product_name, Orders.quantity, Orders.price 
        FROM Orders 
        INNER JOIN Products ON Orders.product_id = Products.product_id
        WHERE Orders.customer_id = ?
    ''', (customer_id,))

    result = cursor.fetchall()
    summary = [f"{product_name}: {quantity} unit(s) at GHS {price:.2f}"
               for product_name, quantity, price in result]

    print(f"\nOrder summary for Customer {customer_id}:\n" + "\n".join(summary))

# Example call for placing orders
# place_order(conn, cursor, 1, 1, 15)

# Example call to get detailed order summary
# get_detailed_order_summary(conn, cursor, 1)

# Close the database connection
conn.close()
