import csv
import json
import os
from connect import get_connection

PHONE_TYPES = {"home", "work", "mobile"}
DEFAULT_GROUP = "Other"

BASE_JOIN_QUERY = """
SELECT
    c.id,
    c.username,
    c.email,
    c.birthday,
    COALESCE(g.name, '') AS group_name,
    c.created_at,
    p.phone,
    p.type
FROM contacts c
LEFT JOIN groups_table g ON g.id = c.group_id
LEFT JOIN phones p ON p.contact_id = c.id
"""

JOIN_SORT_MAP = {
    "1": "c.username ASC, c.id ASC, p.id ASC",
    "2": "c.birthday ASC NULLS LAST, c.username ASC, c.id ASC, p.id ASC",
    "3": "c.created_at ASC, c.id ASC, p.id ASC"
}

CONTACT_SORT_MAP = {
    "1": "c.username ASC, c.id ASC",
    "2": "c.birthday ASC NULLS LAST, c.username ASC, c.id ASC",
    "3": "c.created_at ASC, c.id ASC"
}


def clean(value):
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None


def normalize_phone_type(phone_type):
    phone_type = clean(phone_type)
    if phone_type is None:
        return "mobile"
    phone_type = phone_type.lower()
    if phone_type not in PHONE_TYPES:
        raise ValueError("Phone type must be: home, work, or mobile.")
    return phone_type


def run_sql_file(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        sql = f.read()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()


def create_db_objects():
    try:
        run_sql_file("schema.sql")
        run_sql_file("functions.sql")
        run_sql_file("procedures.sql")
        print("Database schema, functions, and procedures are ready.")
    except Exception as e:
        print("Error creating DB objects:", e)


def sync_phonebook(cur):
    cur.execute("TRUNCATE TABLE phonebook RESTART IDENTITY;")
    cur.execute("""
        INSERT INTO phonebook (username, phone)
        SELECT c.username, p.phone
        FROM contacts c
        JOIN phones p ON p.contact_id = c.id
        ORDER BY c.id, p.id;
    """)


def ensure_group(cur, group_name):
    group_name = clean(group_name) or DEFAULT_GROUP

    cur.execute("""
        INSERT INTO groups_table (name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING;
    """, (group_name,))

    cur.execute("SELECT id FROM groups_table WHERE name = %s;", (group_name,))
    row = cur.fetchone()
    return row[0]


def insert_phone_if_new(cur, contact_id, phone, phone_type):
    phone = clean(phone)
    if not phone:
        return

    phone_type = normalize_phone_type(phone_type)

    cur.execute("""
        INSERT INTO phones (contact_id, phone, type)
        VALUES (%s, %s, %s)
        ON CONFLICT (phone) DO NOTHING;
    """, (contact_id, phone, phone_type))


def upsert_contact_with_phone(cur, username, email, birthday, group_name, phone, phone_type):
    username = clean(username)
    email = clean(email)
    birthday = clean(birthday)
    group_name = clean(group_name) or DEFAULT_GROUP

    if not username:
        raise ValueError("Username is required.")

    group_id = ensure_group(cur, group_name)

    cur.execute("SELECT id FROM contacts WHERE username = %s;", (username,))
    existing = cur.fetchone()

    if existing:
        contact_id = existing[0]
        cur.execute("""
            UPDATE contacts
            SET email = COALESCE(%s, email),
                birthday = COALESCE(%s, birthday),
                group_id = %s
            WHERE id = %s;
        """, (email, birthday, group_id, contact_id))
    else:
        cur.execute("""
            INSERT INTO contacts (username, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (username, email, birthday, group_id))
        contact_id = cur.fetchone()[0]

    insert_phone_if_new(cur, contact_id, phone, phone_type)
    return contact_id


def overwrite_contact_from_json(cur, username, email, birthday, group_name, phones_data):
    username = clean(username)
    email = clean(email)
    birthday = clean(birthday)
    group_name = clean(group_name) or DEFAULT_GROUP

    if not username:
        raise ValueError("Username is required.")

    group_id = ensure_group(cur, group_name)

    cur.execute("SELECT id FROM contacts WHERE username = %s;", (username,))
    existing = cur.fetchone()

    if existing:
        contact_id = existing[0]
        cur.execute("""
            UPDATE contacts
            SET email = %s,
                birthday = %s,
                group_id = %s
            WHERE id = %s;
        """, (email, birthday, group_id, contact_id))
        cur.execute("DELETE FROM phones WHERE contact_id = %s;", (contact_id,))
    else:
        cur.execute("""
            INSERT INTO contacts (username, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (username, email, birthday, group_id))
        contact_id = cur.fetchone()[0]

    for item in phones_data:
        phone = clean(item.get("phone"))
        phone_type = clean(item.get("type")) or "mobile"
        if phone:
            insert_phone_if_new(cur, contact_id, phone, phone_type)


def fetch_rows(where_clause="", params=(), order_by="c.id ASC, p.id ASC"):
    query = BASE_JOIN_QUERY
    if where_clause:
        query += " " + where_clause
    query += f" ORDER BY {order_by};"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()


def print_contacts(rows):
    if not rows:
        print("No contacts found.")
        return

    contacts = {}

    for row in rows:
        contact_id, username, email, birthday, group_name, created_at, phone, phone_type = row

        if contact_id not in contacts:
            contacts[contact_id] = {
                "username": username,
                "email": email,
                "birthday": birthday,
                "group_name": group_name,
                "created_at": created_at,
                "phones": []
            }

        if phone:
            contacts[contact_id]["phones"].append(f"{phone} ({phone_type})")

    print("\nContacts:")
    for contact_id, data in contacts.items():
        phones_text = ", ".join(data["phones"]) if data["phones"] else "No phones"
        print(
            f"\nID: {contact_id}\n"
            f"Username: {data['username']}\n"
            f"Email: {data['email'] or '-'}\n"
            f"Birthday: {data['birthday'] or '-'}\n"
            f"Group: {data['group_name'] or '-'}\n"
            f"Created at: {data['created_at']}\n"
            f"Phones: {phones_text}"
        )


def show_all_contacts():
    try:
        rows = fetch_rows(order_by="c.id ASC, p.id ASC")
        print_contacts(rows)
    except Exception as e:
        print("Error showing contacts:", e)


def insert_from_console():
    try:
        username = input("Enter username: ").strip()
        email = input("Enter email: ").strip()
        birthday = input("Enter birthday (YYYY-MM-DD): ").strip()
        group_name = input("Enter group (Family/Work/Friend/Other): ").strip()
        phone = input("Enter phone: ").strip()
        phone_type = input("Enter phone type (home/work/mobile): ").strip()

        with get_connection() as conn:
            with conn.cursor() as cur:
                upsert_contact_with_phone(
                    cur=cur,
                    username=username,
                    email=email,
                    birthday=birthday,
                    group_name=group_name,
                    phone=phone,
                    phone_type=phone_type
                )
                sync_phonebook(cur)
                conn.commit()

        print("Contact inserted/updated successfully.")
        show_all_contacts()

    except Exception as e:
        print("Error inserting from console:", e)


def insert_from_csv(filename="contacts.csv"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, filename)

    invalid_rows = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            with get_connection() as conn:
                with conn.cursor() as cur:
                    for index, row in enumerate(reader, start=2):
                        username = clean(row.get("username"))
                        email = clean(row.get("email"))
                        birthday = clean(row.get("birthday"))
                        group_name = clean(row.get("group_name") or row.get("group"))
                        phone = clean(row.get("phone"))
                        phone_type = clean(row.get("phone_type") or row.get("type") or "mobile")

                        try:
                            upsert_contact_with_phone(
                                cur=cur,
                                username=username,
                                email=email,
                                birthday=birthday,
                                group_name=group_name,
                                phone=phone,
                                phone_type=phone_type
                            )
                        except Exception as row_error:
                            invalid_rows.append(f"Line {index}: {row_error}")

                    sync_phonebook(cur)
                    conn.commit()

        print("CSV import completed.")

        if invalid_rows:
            print("\nInvalid rows:")
            for item in invalid_rows:
                print(item)
        else:
            print("No invalid rows found.")

        show_all_contacts()

    except FileNotFoundError:
        print("CSV file not found.")
    except Exception as e:
        print("Error importing CSV:", e)


def update_contact_info():
    try:
        show_all_contacts()
        username = input("\nEnter existing username to update: ").strip()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.id, c.username, c.email, c.birthday, COALESCE(g.name, '')
                    FROM contacts c
                    LEFT JOIN groups_table g ON g.id = c.group_id
                    WHERE c.username = %s;
                """, (username,))
                row = cur.fetchone()

                if not row:
                    print("Contact not found.")
                    return

                contact_id, current_username, current_email, current_birthday, current_group = row

                print("Leave field empty to keep current value.")
                new_username = clean(input(f"New username [{current_username}]: ").strip()) or current_username
                new_email = clean(input(f"New email [{current_email or '-'}]: ").strip()) or current_email
                new_birthday = clean(input(f"New birthday [{current_birthday or '-'}]: ").strip()) or current_birthday
                new_group = clean(input(f"New group [{current_group or DEFAULT_GROUP}]: ").strip()) or current_group or DEFAULT_GROUP

                group_id = ensure_group(cur, new_group)

                cur.execute("""
                    UPDATE contacts
                    SET username = %s,
                        email = %s,
                        birthday = %s,
                        group_id = %s
                    WHERE id = %s;
                """, (new_username, new_email, new_birthday, group_id, contact_id))

                sync_phonebook(cur)
                conn.commit()

        print("Contact updated successfully.")
        show_all_contacts()

    except Exception as e:
        print("Error updating contact:", e)


def update_phone():
    try:
        show_all_contacts()
        old_phone = input("\nEnter old phone: ").strip()
        new_phone = input("Enter new phone: ").strip()
        new_type = input("Enter new phone type (home/work/mobile) or leave empty: ").strip()

        with get_connection() as conn:
            with conn.cursor() as cur:
                if clean(new_type):
                    new_type = normalize_phone_type(new_type)
                    cur.execute("""
                        UPDATE phones
                        SET phone = %s,
                            type = %s
                        WHERE phone = %s;
                    """, (new_phone, new_type, old_phone))
                else:
                    cur.execute("""
                        UPDATE phones
                        SET phone = %s
                        WHERE phone = %s;
                    """, (new_phone, old_phone))

                if cur.rowcount == 0:
                    print("Phone not found.")
                    conn.rollback()
                    return

                sync_phonebook(cur)
                conn.commit()

        print("Phone updated successfully.")
        show_all_contacts()

    except Exception as e:
        print("Error updating phone:", e)


def add_phone():
    try:
        contact_name = input("Enter contact username: ").strip()
        phone = input("Enter new phone: ").strip()
        phone_type = normalize_phone_type(input("Enter phone type (home/work/mobile): ").strip())

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL add_phone(%s, %s, %s);", (contact_name, phone, phone_type))
                sync_phonebook(cur)
                conn.commit()

        print("Phone added successfully.")
        show_all_contacts()

    except Exception as e:
        print("Error adding phone:", e)


def move_contact_to_group():
    try:
        contact_name = input("Enter contact username: ").strip()
        group_name = input("Enter new group: ").strip()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL move_to_group(%s, %s);", (contact_name, group_name))
                sync_phonebook(cur)
                conn.commit()

        print("Contact moved to group successfully.")
        show_all_contacts()

    except Exception as e:
        print("Error moving contact to group:", e)


def choose_sort():
    print("\nSort by:")
    print("1. Username")
    print("2. Birthday")
    print("3. Created date")
    choice = input("Choose option: ").strip()

    if choice not in JOIN_SORT_MAP:
        print("Invalid sort option. Default: created date.")
        choice = "3"

    return choice


def paginate_contacts():
    try:
        page_size = int(input("Enter page size: ").strip())
        sort_choice = choose_sort()
        order_contacts = CONTACT_SORT_MAP[sort_choice]
        order_join = JOIN_SORT_MAP[sort_choice]

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM contacts;")
                total_contacts = cur.fetchone()[0]

        if total_contacts == 0:
            print("No contacts found.")
            return

        offset = 0

        while True:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        SELECT c.id
                        FROM contacts c
                        ORDER BY {order_contacts}
                        LIMIT %s OFFSET %s;
                    """, (page_size, offset))
                    ids = [row[0] for row in cur.fetchall()]

                    if not ids:
                        print("No contacts on this page.")
                        return

                    cur.execute(f"""
                        {BASE_JOIN_QUERY}
                        WHERE c.id = ANY(%s)
                        ORDER BY {order_join};
                    """, (ids,))
                    rows = cur.fetchall()

            current_page = offset // page_size + 1
            total_pages = (total_contacts + page_size - 1) // page_size

            print(f"\n--- Page {current_page} of {total_pages} ---")
            print_contacts(rows)

            command = input("\nType next / prev / quit: ").strip().lower()

            if command == "next":
                if offset + page_size >= total_contacts:
                    print("This is the last page.")
                else:
                    offset += page_size
            elif command == "prev":
                if offset == 0:
                    print("This is the first page.")
                else:
                    offset -= page_size
            elif command == "quit":
                break
            else:
                print("Unknown command.")

    except Exception as e:
        print("Error in pagination:", e)


def query_contacts():
    print("\nQuery options:")
    print("1. Show all contacts")
    print("2. Filter by group")
    print("3. Search by email")
    print("4. Search by pattern (name, email, phone)")
    print("5. Show sorted contacts")
    print("6. Show contacts with pagination")
    choice = input("Choose option: ").strip()

    try:
        if choice == "1":
            show_all_contacts()

        elif choice == "2":
            group_name = input("Enter group name: ").strip()
            rows = fetch_rows(
                where_clause="WHERE COALESCE(g.name, '') ILIKE %s",
                params=(f"%{group_name}%",),
                order_by="c.username ASC, p.id ASC"
            )
            print_contacts(rows)

        elif choice == "3":
            email = input("Enter email pattern: ").strip()
            rows = fetch_rows(
                where_clause="WHERE COALESCE(c.email, '') ILIKE %s",
                params=(f"%{email}%",),
                order_by="c.username ASC, p.id ASC"
            )
            print_contacts(rows)

        elif choice == "4":
            pattern = input("Enter pattern: ").strip()
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
                    rows = cur.fetchall()
            print_contacts(rows)

        elif choice == "5":
            sort_choice = choose_sort()
            rows = fetch_rows(order_by=JOIN_SORT_MAP[sort_choice])
            print_contacts(rows)

        elif choice == "6":
            paginate_contacts()

        else:
            print("Invalid choice.")

    except Exception as e:
        print("Error querying contacts:", e)


def delete_contact():
    try:
        print("\nDelete options:")
        print("1. Delete contact by username")
        print("2. Delete by phone")
        choice = input("Choose option: ").strip()

        with get_connection() as conn:
            with conn.cursor() as cur:
                if choice == "1":
                    username = input("Enter username to delete: ").strip()
                    cur.execute("DELETE FROM contacts WHERE username = %s;", (username,))

                    if cur.rowcount == 0:
                        print("Contact not found.")
                        conn.rollback()
                        return

                elif choice == "2":
                    phone = input("Enter phone to delete: ").strip()

                    cur.execute("SELECT contact_id FROM phones WHERE phone = %s;", (phone,))
                    row = cur.fetchone()

                    if not row:
                        print("Phone not found.")
                        conn.rollback()
                        return

                    contact_id = row[0]

                    cur.execute("DELETE FROM phones WHERE phone = %s;", (phone,))
                    cur.execute("SELECT COUNT(*) FROM phones WHERE contact_id = %s;", (contact_id,))
                    phones_left = cur.fetchone()[0]

                    if phones_left == 0:
                        cur.execute("DELETE FROM contacts WHERE id = %s;", (contact_id,))

                else:
                    print("Invalid choice.")
                    conn.rollback()
                    return

                sync_phonebook(cur)
                conn.commit()
                print("Delete operation completed.")

        show_all_contacts()

    except Exception as e:
        print("Error deleting contact:", e)


def export_to_json(filename="contacts.json"):
    try:
        rows = fetch_rows(order_by="c.id ASC, p.id ASC")

        contacts = {}

        for row in rows:
            contact_id, username, email, birthday, group_name, created_at, phone, phone_type = row

            if contact_id not in contacts:
                contacts[contact_id] = {
                    "username": username,
                    "email": email,
                    "birthday": str(birthday) if birthday else None,
                    "group": group_name or None,
                    "created_at": str(created_at) if created_at else None,
                    "phones": []
                }

            if phone:
                contacts[contact_id]["phones"].append({
                    "phone": phone,
                    "type": phone_type
                })

        data = list(contacts.values())

        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"Contacts exported to {filename} successfully.")

    except Exception as e:
        print("Error exporting JSON:", e)


def import_from_json(filename="contacts.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, filename)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        with get_connection() as conn:
            with conn.cursor() as cur:
                for item in data:
                    username = clean(item.get("username"))
                    email = clean(item.get("email"))
                    birthday = clean(item.get("birthday"))
                    group_name = clean(item.get("group")) or DEFAULT_GROUP
                    phones_data = item.get("phones", [])

                    cur.execute("SELECT id FROM contacts WHERE username = %s;", (username,))
                    existing = cur.fetchone()

                    if existing:
                        action = input(
                            f'Contact "{username}" already exists. Type skip or overwrite: '
                        ).strip().lower()

                        while action not in {"skip", "overwrite"}:
                            action = input('Please type only skip or overwrite: ').strip().lower()

                        if action == "skip":
                            continue

                    overwrite_contact_from_json(
                        cur=cur,
                        username=username,
                        email=email,
                        birthday=birthday,
                        group_name=group_name,
                        phones_data=phones_data
                    )

                sync_phonebook(cur)
                conn.commit()

        print("JSON import completed successfully.")
        show_all_contacts()

    except FileNotFoundError:
        print("JSON file not found.")
    except Exception as e:
        print("Error importing JSON:", e)


def menu():
    create_db_objects()

    while True:
        print("\n--- EXTENDED PHONEBOOK MENU ---")
        print("1. Import contacts from CSV")
        print("2. Insert contact from console")
        print("3. Update contact info")
        print("4. Update existing phone")
        print("5. Add new phone to existing contact")
        print("6. Move contact to another group")
        print("7. Query / Search / Filter contacts")
        print("8. Delete by username or phone")
        print("9. Export all contacts to JSON")
        print("10. Import contacts from JSON")
        print("11. Show all contacts")
        print("12. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            insert_from_csv("contacts.csv")
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            update_contact_info()
        elif choice == "4":
            update_phone()
        elif choice == "5":
            add_phone()
        elif choice == "6":
            move_contact_to_group()
        elif choice == "7":
            query_contacts()
        elif choice == "8":
            delete_contact()
        elif choice == "9":
            export_to_json("contacts.json")
        elif choice == "10":
            import_from_json("contacts.json")
        elif choice == "11":
            show_all_contacts()
        elif choice == "12":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    menu()