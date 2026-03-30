CREATE OR REPLACE PROCEDURE upsert_contact(p_username VARCHAR(100), p_phone VARCHAR(20))
LANGUAGE plpgsql
AS $$
BEGIN
    IF TRIM(p_username) = '' OR TRIM(p_phone) = '' THEN
        RAISE EXCEPTION 'Username and phone cannot be empty';
    END IF;

    IF EXISTS (SELECT 1 FROM phonebook WHERE username = p_username) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE username = p_username;
    ELSE
        INSERT INTO phonebook(username, phone)
        VALUES (p_username, p_phone);
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE insert_many_contacts(
    IN p_usernames TEXT[],
    IN p_phones TEXT[],
    INOUT p_invalid_data TEXT[] DEFAULT ARRAY[]::TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    v_username TEXT;
    v_phone TEXT;
BEGIN
    p_invalid_data := ARRAY[]::TEXT[];

    IF COALESCE(array_length(p_usernames, 1), 0) <> COALESCE(array_length(p_phones, 1), 0) THEN
        RAISE EXCEPTION 'Usernames and phones arrays must have the same length';
    END IF;

    FOR i IN 1 .. COALESCE(array_length(p_usernames, 1), 0) LOOP
        v_username := TRIM(COALESCE(p_usernames[i], ''));
        v_phone := TRIM(COALESCE(p_phones[i], ''));

        IF v_username = '' OR v_phone !~ '^\+?[0-9]{10,15}$' THEN
            p_invalid_data := array_append(
                p_invalid_data,
                FORMAT('username=%s, phone=%s', v_username, v_phone)
            );
        ELSE
            CALL upsert_contact(v_username, v_phone);
        END IF;
    END LOOP;
END;
$$;


CREATE OR REPLACE PROCEDURE delete_contact_by_value(p_value TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE username = p_value OR phone = p_value;
END;
$$;


CREATE OR REPLACE PROCEDURE update_contact_by_id(
    p_id INT,
    p_new_username VARCHAR(100),
    p_new_phone VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM phonebook WHERE id = p_id) THEN
        RAISE EXCEPTION 'Contact with id % not found', p_id;
    END IF;

    UPDATE phonebook
    SET
        username = CASE
            WHEN p_new_username IS NULL OR TRIM(p_new_username) = '' THEN username
            ELSE p_new_username
        END,
        phone = CASE
            WHEN p_new_phone IS NULL OR TRIM(p_new_phone) = '' THEN phone
            ELSE p_new_phone
        END
    WHERE id = p_id;
END;
$$;