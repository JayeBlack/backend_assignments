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
    def wrapper(*args, **kwargs):
        product_id = kwargs.get('product_id')
        cursor.execute("SELECT stock FROM Products WHERE product_id=?", (product_id,))
        result = cursor.fetchone()
        if result and result[0] > 0:
            return func(*args, **kwargs)
        else:
            print("Product not found or out of stock")

    return wrapper


# Lambda for discounts (10%)
discount = lambda total_items: 0.10 if total_items > 10 else 0


@validate_user_input
def place_order(customer_id, product_id, quantity):
    cursor.execute("SELECT price FROM Products WHERE product_id=?", (product_id,))
    original_price_per_item = cursor.fetchone()

    # Check if the product was found in the database
    if original_price_per_item is None:
        print(f"Error: Product with ID '{product_id}' not found.")
        return  # Exit the function if the product is not found

    # Extract the price from the tuple returned by fetchone()
    original_price_per_item = original_price_per_item[0]

    total_price = original_price_per_item * quantity
    discount_percentage = discount(quantity)  # Calculate discount
    discount_amount = total_price * discount_percentage  # Calculate discount amount
    final_price = total_price - discount_amount  # Calculate final price after discount

    # Save the order to the database
    cursor.execute('''INSERT INTO Orders (customer_id, product_id, price, quantity) 
                      VALUES (?, ?, ?, ?)''',
                   (customer_id, product_id, final_price, quantity))
    conn.commit()  # Commit the transaction to save changes

    print(f"Order placed for {quantity} unit(s) of product ID {product_id}. Total Price: GHS {final_price:.2f}")


# Example of placing orders with test cases
place_order(customer_id=1, product_id=1, quantity=15)  # Bulk order with discount
place_order(customer_id=2, product_id=5, quantity=8)  # No discount
place_order(customer_id=3, product_id=2, quantity=5)  # No discount


# Generator to stream order history for each customer
def get_order_history(customer_id):
    cursor.execute("SELECT * FROM Orders WHERE customer_id=?", (customer_id,))
    while True:
        order = cursor.fetchone()
        if order is None:
            break
        yield order


# Display order history for a customer
print("\nOrder History for Customer 1:")
for order in get_order_history(1):
    print(order)


# List Comprehension to summarize orders
def get_detailed_order_summary(customer_id):
    cursor.execute('''
        SELECT Products.name AS product_name, Orders.quantity, Orders.price 
        FROM Orders 
        INNER JOIN Products ON Orders.product_id = Products.product_id
        WHERE Orders.customer_id = ?
    ''', (customer_id,))

    # Fetch all rows and process with list comprehension
    result = cursor.fetchall()
    summary = [f"{product_name}: {quantity} unit(s) at GHS {price:.2f}"
               for product_name, quantity, price in result]

    print(f"\nOrder summary for Customer {customer_id}:\n" + "\n".join(summary))



get_detailed_order_summary(1)
# Close the database connection
conn.close()
