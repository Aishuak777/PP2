CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p_pattern TEXT)
RETURNS TABLE (
    id INT,
    username VARCHAR(100),
    phone VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.username, p.phone
    FROM phonebook p
    WHERE p.username ILIKE '%' || p_pattern || '%'
       OR p.phone ILIKE '%' || p_pattern || '%'
    ORDER BY p.id;
END;
$$;


CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE (
    id INT,
    username VARCHAR(100),
    phone VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_limit <= 0 THEN
        RAISE EXCEPTION 'Limit must be greater than 0';
    END IF;

    IF p_offset < 0 THEN
        RAISE EXCEPTION 'Offset cannot be negative';
    END IF;

    RETURN QUERY
    SELECT p.id, p.username, p.phone
    FROM phonebook p
    ORDER BY p.id
    LIMIT p_limit OFFSET p_offset;
END;
$$;