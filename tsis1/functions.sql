CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id INTEGER,
    username VARCHAR(100),
    email VARCHAR(120),
    birthday DATE,
    group_name VARCHAR(50),
    created_at TIMESTAMP,
    phone VARCHAR(20),
    phone_type VARCHAR(20)
)
LANGUAGE SQL
AS $$
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
    WHERE c.username ILIKE '%' || p_query || '%'
       OR COALESCE(c.email, '') ILIKE '%' || p_query || '%'
       OR COALESCE(p.phone, '') ILIKE '%' || p_query || '%'
    ORDER BY c.username, p.phone;
$$;