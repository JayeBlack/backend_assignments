import sqlite3
from e_commerce import place_order, get_order_history, get_detailed_order_summary


# Connect to the SQLite database
def connect_to_db():
    return sqlite3.connect('ecommerce.db')


# Display menu options for the user
def display_menu():
    print("Welcome to the E-Commerce Order Management System")
    print("Please choose an option:")
    print("1. Place an Order")
    print("2. Retrieve Order History")
    print("3. Get Detailed Order Summary")
    print("4. Exit")


# Main function to control the flow of the menu system
def main():
    conn = connect_to_db()
    cursor = conn.cursor()

    while True:
        display_menu()
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            customer_id = int(input("Enter Customer ID: "))
            product_id = int(input("Enter Product ID: "))
            quantity = int(input("Enter Quantity: "))
            place_order(conn, cursor, customer_id, product_id, quantity)

        elif choice == '2':
            customer_id = int(input("Enter Customer ID to retrieve order history: "))
            print("\nOrder History:")
            for order in get_order_history(conn, cursor, customer_id):
                print(order)

        elif choice == '3':
            customer_id = int(input("Enter Customer ID for detailed order summary: "))
            get_detailed_order_summary(conn, cursor, customer_id)

        elif choice == '4':
            print("Exiting the system. Thank you!")
            break

        else:
            print("Invalid choice. Please try again.")

    conn.close()


# Entry point to start the program
if __name__ == "__main__":
    main()
