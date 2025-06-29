from sqlalchemy import text

def get_discounted_products_query():
    return text("""
        SELECT 
            u.id AS client_id,
            u.name AS client_name,
            u.email AS client_email,
            ST_Y(u.coordinates::geometry) AS client_lat,
            ST_X(u.coordinates::geometry) AS client_lng,
            u.radius AS client_radius,
            s.name AS shop_name,
            p.name AS product_name,
            p.price AS original_price,
            ROUND((p.price * (1 - p.discount / 100.0))::numeric, 2) AS discounted_price
        FROM "user" u
        JOIN shop s 
            ON ST_DWithin(s.coordinates, u.coordinates, u.radius * 1000)
            AND s.state = 'accepted'
        JOIN product p 
            ON p.shop_id = s.id
        WHERE 
            u.type = 'client'
            AND u.coordinates IS NOT NULL
            AND u.radius IS NOT NULL
            AND p.has_discount = TRUE
    """)
