import sqlite3

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Tables needed:
# 1.Customers
# 2. Orders
# 3. Products

# Creating the Customers Table
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS Customers(
        customer_id INTEGER PRIMARY KEY ,
        name text not null,
        email text unique not null
    )'''
)

# Creating the Orders Table
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS Orders(
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_name TEXT,
        price REAL,
        quantity INTEGER,
        FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)

    )
    '''
)

# Creating the Products Tabl
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS Products(
        product_id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        stock INTEGER
        )
    '''
)
conn.commit()
conn.close()


# Decorator to validate user input
def validate_user_input(func):
    def wrapper(*args, **kwargs):
        product = kwargs.get('product')
        conn = sqlite3.connect("ecommerce.db")
        cursor = conn.cursor()
        cursor.execute("SELECT stock from Products WHERE name=?", (product,))
        result = cursor.fetchone()
        if result and result[0] > 0:
            return func(*args, **kwargs)
        else:
            print("Product not found")
        conn.close()

    return wrapper


# Lambda for discounts(10%)
discount = lambda total_items: 0.10 if total_items > 10 else 0
print(discount(45))
print(discount(5))


@validate_user_input
def place_order(customer_id, product, quantity):
    cursor.execute("SELECT price FROM Products WHERE name=?", (product,))
    original_price_per_item = cursor.fetchone()
    # Check if the product was found in the database
    if original_price_per_item is None:
        print(f"Error: Product '{product}' not found.")
        return  # Exit the function if the product is not found

    # Extract the price from the tuple returned by fetchone()
    original_price_per_item = original_price_per_item[0]

    total_price = original_price_per_item * quantity
    discount_percentage = discount(quantity)  # Calculate discount
    discount_amount = total_price * discount_percentage  # Calculate discount amount
    final_price = total_price - discount_amount  # Calculate final price after discount

    # Here you would include logic to save the order to the database
    print(f"Order placed for {quantity} {product}(s). Total Price: ${final_price:.2f}")


# Example of placing an order
place_order(1, "Product A", 12)  # More than 10 items
place_order(1, "Product B", 8)  # 8 items


# Generator to stream order history
def stream_order_history(customer_id):
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Orders WHERE customer_id=?", (customer_id,))
    while True:
        order = cursor.fetchone()
        if order is None:
            break
        yield order
    conn.close()


# Fetching our orders
for order in stream_order_history(1):
    print(order)
