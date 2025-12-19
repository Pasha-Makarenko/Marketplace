Аналітика та приклади запитів
=============================

Топ рейтингових товарів
-----------------------
Бізнес-питання: показати активні товари в порядку середнього рейтингу та кількості відгуків.

SQL (використовується в `ProductAnalyticsQuery.get_top_rated_products`):
```
WITH product_ratings AS (
    SELECT
        p.product_id,
        p.name,
        p.price,
        AVG(rt.value) AS avg_rating,
        COUNT(rv.review_id) AS review_count
    FROM products p
    LEFT JOIN ratings rt ON rt.product_id = p.product_id
    LEFT JOIN reviews rv ON rv.product_id = p.product_id
    WHERE p.is_active = true
    GROUP BY p.product_id, p.name, p.price
)
SELECT COALESCE(
    json_agg(
        json_build_object(
            'id', pr.product_id,
            'name', pr.name,
            'price', pr.price,
            'avg_rating', COALESCE(pr.avg_rating, 0),
            'review_count', pr.review_count
        )
        ORDER BY pr.avg_rating DESC NULLS LAST,
            pr.review_count DESC
    ),
    '[]'::json
)
FROM (
    SELECT *
    FROM product_ratings
    ORDER BY avg_rating DESC NULLS LAST, review_count DESC
    LIMIT :limit
) pr;
```
Форма результату: масив об’єктів `{id, name, price, avg_rating, review_count}`.

Товари з низьким складом
------------------------
Бізнес-питання: показати активні товари з невеликим залишком.

SQL (в `ProductAnalyticsQuery.get_low_stock_products`):
```
SELECT COALESCE(
    json_agg(
        json_build_object(
            'id', p.product_id,
            'name', p.name,
            'stock_quantity', p.stock_quantity,
            'seller_id', p.owner_id
        )
        ORDER BY p.stock_quantity ASC
    ),
    '[]'::json
)
FROM products p
WHERE p.stock_quantity <= :threshold AND p.is_active = true;
```
Параметр: `:threshold` (типово 5). Повертає JSON-масив.

Продуктивність продавців
------------------------
Бізнес-питання: скільки товарів та замовлень у кожного продавця.

SQL (спрощено з `seller_analytics.py`):
```
SELECT
    s.seller_id,
    s.store_name,
    COUNT(DISTINCT p.product_id) AS product_count,
    COUNT(DISTINCT o.order_id) AS order_count
FROM seller_profiles s
LEFT JOIN products p ON p.owner_id = s.seller_id
LEFT JOIN orders o ON o.user_id = s.user_id
GROUP BY s.seller_id, s.store_name
ORDER BY product_count DESC, order_count DESC;
```
Корисно для адмінських дашбордів.

Розподіл по категоріях
----------------------
Бізнес-питання: скільки товарів у кожній категорії.

SQL (з `category_analytics.py`):
```
SELECT
    c.category_id,
    c.name,
    COUNT(p.product_id) AS product_count
FROM categories c
LEFT JOIN products p ON p.category_id = c.category_id
GROUP BY c.category_id, c.name
ORDER BY product_count DESC;
```
Повертає рядки по категоріях з кількістю товарів.

Денний дохід
------------
Бізнес-питання: дохід на день (з `order_queries.py`):
```
SELECT
    DATE_TRUNC('day', o.created_at) AS day,
    SUM(oi.quantity * oi.price_at_purchase) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY DATE_TRUNC('day', o.created_at)
ORDER BY day DESC;
```
Показує денний дохід за завершеними замовленнями.

