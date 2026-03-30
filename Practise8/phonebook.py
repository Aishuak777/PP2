import csv
import os
from connect import get_connection


def print_contacts(rows):
    if not rows:
        print("No contacts found.")
        return

    print("\nContacts:")
    for row in rows:
        print(f"ID: {row[0]}, Username: {row[1]}, Phone: {row[2]}")


def create_table():
    query = """
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL,
        phone VARCHAR(20) UNIQUE NOT NULL
    );
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()
        print("Table 'phonebook' is ready.")
    except Exception as e:
        print("Error creating table:", e)


def create_db_objects():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        functions_path = os.path.join(base_dir, "functions.sql")
        procedures_path = os.path.join(base_dir, "procedures.sql")

        with get_connection() as conn:
            with conn.cursor() as cur:
                with open(functions_path, "r", encoding="utf-8") as f:
                    cur.execute(f.read())

                with open(procedures_path, "r", encoding="utf-8") as f:
                    cur.execute(f.read())

                conn.commit()

        print("Functions and procedures are ready.")
    except Exception as e:
        print("Error creating functions/procedures:", e)


def show_all_contacts():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM phonebook ORDER BY id;")
                rows = cur.fetchall()
                print_contacts(rows)
    except Exception as e:
        print("Error showing contacts:", e)


def insert_from_console():
    username = input("Enter username: ").strip()
    phone = input("Enter phone: ").strip()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL upsert_contact(%s, %s);", (username, phone))
                conn.commit()

        print("Contact inserted/updated successfully.")
        show_all_contacts()
    except Exception as e:
        print("Error inserting contact:", e)


def insert_from_csv(filename):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)

        usernames = []
        phones = []

        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                usernames.append(row["username"].strip())
                phones.append(row["phone"].strip())

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "CALL insert_many_contacts(%s, %s, %s);",
                    (usernames, phones, [])
                )

                invalid_data = []
                result = cur.fetchone()
                if result and result[0]:
                    invalid_data = result[0]

                conn.commit()

        print("CSV data processed successfully.")

        if invalid_data:
            print("\nIncorrect data:")
            for item in invalid_data:
                print(item)
        else:
            print("No incorrect data found.")

        show_all_contacts()

    except FileNotFoundError:
        print("CSV file not found.")
    except Exception as e:
        print("Error inserting from CSV:", e)


def update_contact():
    try:
        show_all_contacts()
        contact_id = input("\nEnter ID of contact to update: ").strip()

        print("\nWhat do you want to update?")
        print("1. Username")
        print("2. Phone")
        print("3. Both")
        choice = input("Choose option: ").strip()

        new_username = None
        new_phone = None

        if choice == "1":
            new_username = input("Enter new username: ").strip()
        elif choice == "2":
            new_phone = input("Enter new phone: ").strip()
        elif choice == "3":
            new_username = input("Enter new username: ").strip()
            new_phone = input("Enter new phone: ").strip()
        else:
            print("Invalid choice.")
            return

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "CALL update_contact_by_id(%s, %s, %s);",
                    (int(contact_id), new_username, new_phone)
                )
                conn.commit()

        print("Contact updated successfully.")
        show_all_contacts()

    except Exception as e:
        print("Error updating contact:", e)


def query_contacts():
    print("\nQuery options:")
    print("1. Show all contacts")
    print("2. Search by pattern")
    print("3. Show contacts with pagination")
    choice = input("Choose option: ").strip()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if choice == "1":
                    cur.execute("SELECT * FROM phonebook ORDER BY id;")

                elif choice == "2":
                    pattern = input("Enter pattern (username or phone): ").strip()
                    cur.execute("SELECT * FROM get_contacts_by_pattern(%s);", (pattern,))

                elif choice == "3":
                    limit = int(input("Enter LIMIT: ").strip())
                    offset = int(input("Enter OFFSET: ").strip())
                    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s);", (limit, offset))

                else:
                    print("Invalid choice.")
                    return

                rows = cur.fetchall()
                print_contacts(rows)

    except Exception as e:
        print("Error querying contacts:", e)


def delete_contact():
    try:
        show_all_contacts()
        value = input("\nEnter username or phone to delete: ").strip()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL delete_contact_by_value(%s);", (value,))
                conn.commit()

        print("Delete operation completed.")
        show_all_contacts()

    except Exception as e:
        print("Error deleting contact:", e)


def menu():
    create_table()
    create_db_objects()

    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Insert data from CSV")
        print("2. Insert data from console")
        print("3. Update contact by ID")
        print("4. Query contacts")
        print("5. Delete contact by username or phone")
        print("6. Show all contacts")
        print("7. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            insert_from_csv("contacts.csv")
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            update_contact()
        elif choice == "4":
            query_contacts()
        elif choice == "5":
            delete_contact()
        elif choice == "6":
            show_all_contacts()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    menu()