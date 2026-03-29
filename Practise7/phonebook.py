import csv
import os
from connect import get_connection

def show_all_contacts():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM phonebook ORDER BY id;")
                rows = cur.fetchall()

                if not rows:
                    print("No contacts found.")
                else:
                    print("\nContacts:")
                    for row in rows:
                        print(f"ID: {row[0]}, Username: {row[1]}, Phone: {row[2]}")
    except Exception as e:
        print("Error showing contacts:", e)
        
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


def insert_from_csv(filename):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)

        with get_connection() as conn:
            with conn.cursor() as cur:
                with open(file_path, "r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        username = row["username"].strip()
                        phone = row["phone"].strip()

                        cur.execute(
                            """
                            INSERT INTO phonebook (username, phone)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING;
                            """,
                            (username, phone),
                        )

                conn.commit()
        print("Data inserted from CSV successfully.")
    except FileNotFoundError:
        print("CSV file not found.")
    except Exception as e:
        print("Error inserting from CSV:", e)


def insert_from_console():
    username = input("Enter username: ").strip()
    phone = input("Enter phone: ").strip()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO phonebook (username, phone)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                """, (username, phone))
                conn.commit()
        print("Contact added successfully.")
    except Exception as e:
        print("Error inserting contact:", e)


def update_contact():
    try:
        show_all_contacts()

        contact_id = input("\nEnter ID of contact to update: ").strip()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM phonebook WHERE id = %s;", (contact_id,))
                contact = cur.fetchone()

                if not contact:
                    print("Contact with this ID not found.")
                    return

                print("\nWhat do you want to update?")
                print("1. Username")
                print("2. Phone")
                choice = input("Choose option: ").strip()

                if choice == "1":
                    new_username = input("Enter new username: ").strip()
                    cur.execute(
                        "UPDATE phonebook SET username = %s WHERE id = %s;",
                        (new_username, contact_id)
                    )
                    conn.commit()
                    print("Username updated successfully.")

                elif choice == "2":
                    new_phone = input("Enter new phone: ").strip()
                    cur.execute(
                        "UPDATE phonebook SET phone = %s WHERE id = %s;",
                        (new_phone, contact_id)
                    )
                    conn.commit()
                    print("Phone updated successfully.")

                else:
                    print("Invalid choice.")
                    return

                print("\nUpdated table:")
                show_all_contacts()

    except Exception as e:
        print("Error updating contact:", e)


def query_contacts():
    print("\nQuery options:")
    print("1. Show all contacts")
    print("2. Search by username")
    print("3. Search by phone prefix")
    choice = input("Choose option: ").strip()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if choice == "1":
                    cur.execute("SELECT * FROM phonebook ORDER BY id;")

                elif choice == "2":
                    name = input("Enter username to search: ").strip()
                    cur.execute("""
                        SELECT * FROM phonebook
                        WHERE username ILIKE %s
                        ORDER BY id;
                    """, (f"%{name}%",))

                elif choice == "3":
                    prefix = input("Enter phone prefix: ").strip()
                    cur.execute("""
                        SELECT * FROM phonebook
                        WHERE phone LIKE %s
                        ORDER BY id;
                    """, (f"{prefix}%",))

                else:
                    print("Invalid choice.")
                    return

                rows = cur.fetchall()

                if not rows:
                    print("No contacts found.")
                else:
                    print("\nContacts:")
                    for row in rows:
                        print(f"ID: {row[0]}, Username: {row[1]}, Phone: {row[2]}")
    except Exception as e:
        print("Error querying contacts:", e)


def delete_contact():
    try:
        show_all_contacts()

        contact_id = input("\nEnter ID of contact to delete: ").strip()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM phonebook WHERE id = %s;", (contact_id,))
                contact = cur.fetchone()

                if not contact:
                    print("Contact with this ID not found.")
                    return

                cur.execute("DELETE FROM phonebook WHERE id = %s;", (contact_id,))
                conn.commit()

                print("Contact deleted successfully.")
                print("\nUpdated table:")
                show_all_contacts()

    except Exception as e:
        print("Error deleting contact:", e)


def menu():
    create_table()

    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Insert data from CSV")
        print("2. Insert data from console")
        print("3. Update contact")
        print("4. Query contacts")
        print("5. Delete contact")
        print("6. Exit")

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
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    menu()