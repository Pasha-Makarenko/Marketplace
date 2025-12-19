Аналітика та приклади запитів
=============================

Запит 1: Топ рейтингових товарів (ProductAnalyticsQuery.get_top_rated_products)
-------------------------------------------------------------------------------
Бізнес-питання: показати активні товари за середнім рейтингом та кількістю відгуків.

```sql
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
Пояснення:
- CTE `product_ratings`: для кожного активного товару робить LEFT JOIN з `ratings` і `reviews`, рахує `AVG(rt.value)` та `COUNT(rv.review_id)`.
- Далі вибирає все з CTE, сортує за `avg_rating` DESC (NULLS LAST), потім за `review_count` DESC, обмежує `LIMIT :limit`.
- Обгортає результат у `json_agg/json_build_object`, повертає JSON-масив товарів з полями id, name, price, avg_rating, review_count.

Запит 2: Товари з низьким складом (ProductAnalyticsQuery.get_low_stock_products)
-------------------------------------------------------------------------------
Бізнес-питання: знайти активні товари з малим залишком.

```sql
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
Пояснення (по кроках):
- Фільтрує `products` за `stock_quantity <= :threshold` і `is_active = true`.
- Сортує за `stock_quantity` ASC, будує JSON через `json_agg/json_build_object`.
- Повертає масив з id, name, stock_quantity, seller_id.

Запит 3: Розподіл по категоріях (CategoryAnalyticsQuery.get_category_distribution)
---------------------------------------------------------------------------------
Бізнес-питання: скільки товарів у категоріях і яка середня ціна.

```sql
WITH category_stats AS (
    SELECT
        c.category_id,
        c.name,
        COUNT(p.product_id) AS product_count,
        COALESCE(AVG(p.price), 0) AS avg_price
    FROM categories c
    LEFT JOIN products p
        ON p.category_id = c.category_id AND p.is_active = true
    GROUP BY c.category_id, c.name
)
SELECT COALESCE(
    json_agg(
        json_build_object(
            'id', cs.category_id,
            'name', cs.name,
            'product_count', cs.product_count,
            'avg_price', cs.avg_price
        )
        ORDER BY cs.product_count DESC
    ),
    '[]'::json
)
FROM category_stats cs;
```
Пояснення:
- CTE `category_stats`: LEFT JOIN активних продуктів до категорій, рахує `COUNT(product_id)` і `AVG(price)` (COALESCE до 0), групує по категорії.
- З CTE формує JSON-агрегацію, сортує за `product_count` DESC.
- Повертає масив з id, name, product_count, avg_price.

Запит 4: Топ продавців (SellerAnalyticsQuery.get_top_sellers)
-------------------------------------------------------------
Бізнес-питання: показати активних продавців за середнім рейтингом та кількістю товарів.

```sql
WITH seller_stats AS (
    SELECT
        s.seller_id,
        s.store_name,
        COUNT(DISTINCT p.product_id) AS total_products,
        AVG(rat.value) AS avg_seller_rating,
        COUNT(rat.rating_id) AS total_ratings
    FROM seller_profiles s
    LEFT JOIN products p
        ON p.owner_id = s.seller_id AND p.is_active = true
    LEFT JOIN ratings rat ON rat.product_id = p.product_id
    WHERE s.is_active = true
    GROUP BY s.seller_id, s.store_name
)
SELECT COALESCE(
    json_agg(
        json_build_object(
            'id', ss.seller_id,
            'store_name', ss.store_name,
            'total_products', ss.total_products,
            'average_rating', COALESCE(ss.avg_seller_rating, 0),
            'total_ratings', ss.total_ratings
        )
        ORDER BY ss.avg_seller_rating DESC NULLS LAST
    ),
    '[]'::json
)
FROM (
    SELECT * FROM seller_stats LIMIT :limit
) ss;
```
Пояснення:
- CTE `seller_stats`: для активних продавців робить LEFT JOIN активних продуктів і їхніх рейтинґів; рахує кількість продуктів, `AVG(rat.value)` та `COUNT(rat.rating_id)`.
- З CTE вибирає, обмежує `LIMIT :limit`, сортує за `avg_seller_rating` DESC (NULLS LAST).
- Формує JSON-агрегацію з полями id, store_name, total_products, average_rating, total_ratings.

Запит 5: Замовлення користувача (UserOrdersQuery.fetch)
--------------------------------------------------------
Бізнес-питання: отримати замовлення поточного користувача з сумою та кількістю позицій.

```sql
WITH order_totals AS (
    SELECT
        o.order_id,
        o.status,
        o.created_at,
        o.updated_at,
        COALESCE(
            SUM(oi.price_at_purchase * oi.quantity),
            0
        ) AS total_amount,
        COALESCE(SUM(oi.quantity), 0) AS items_count
    FROM orders o
    LEFT JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.user_id = :user_id
    GROUP BY o.order_id, o.status, o.created_at, o.updated_at
)
SELECT COALESCE(
    json_agg(
        json_build_object(
            'id', ot.order_id,
            'status', ot.status,
            'created_at', ot.created_at,
            'updated_at', ot.updated_at,
            'total_amount', ot.total_amount,
            'items_count', ot.items_count
        )
        ORDER BY ot.created_at DESC
    ),
    '[]'::json
) AS orders_json
FROM order_totals ot;
```
Пояснення:
- CTE `order_totals`: LEFT JOIN `order_items` до замовлень користувача (`:user_id`), рахує `SUM(price_at_purchase*quantity)` і `SUM(quantity)` по кожному замовленню.
- Групує по order_id, статусу, created_at, updated_at.
- З CTE формує JSON-агрегацію, сортує за `created_at` DESC; повертає масив замовлень із сумою та кількістю позицій.

Запит 6: Статистика статусів замовлень (OrderStatusStatsQuery.fetch)
--------------------------------------------------------------------
Бізнес-питання: скільки замовлень у кожному статусі.

```sql
SELECT COALESCE(json_object_agg(status, cnt), '{}'::json) AS stats
FROM (
    SELECT status, COUNT(*) AS cnt
    FROM orders
    GROUP BY status
) s;
```
Пояснення (по кроках):
- Внутрішній запит групує `orders` за `status`, рахує `COUNT(*)`.
- Зовнішній шар перетворює пари статус→кількість у JSON-об’єкт через `json_object_agg`, COALESCE до порожнього `{}`.

Запит 7: Денний дохід (DailyRevenueQuery.fetch)
----------------------------------------------
Бізнес-питання: дохід за днями для оплачених замовлень за останні N днів.

```sql
WITH daily AS (
    SELECT
        DATE_TRUNC('day', o.paid_at) AS day,
        SUM(oi.price_at_purchase * oi.quantity) AS revenue,
        COUNT(DISTINCT o.order_id) AS orders
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.paid_at IS NOT NULL
      AND o.paid_at >= :since
    GROUP BY DATE_TRUNC('day', o.paid_at)
)
SELECT COALESCE(
    json_agg(
        json_build_object(
            'day', to_char(day, 'YYYY-MM-DD'),
            'revenue', revenue,
            'orders', orders
        )
        ORDER BY day DESC
    ),
    '[]'::json
) AS revenue_json
FROM daily;
```
Пояснення:
- CTE `daily`: бере оплачені замовлення (`paid_at IS NOT NULL`), фільтрує за `paid_at >= :since`; JOIN з `order_items`; групує по дню `DATE_TRUNC('day', paid_at)`; рахує `SUM(price_at_purchase*quantity)` та `COUNT(DISTINCT order_id)`.
- З CTE формує JSON-агрегацію, сортує за днем DESC, приводить день до формату `YYYY-MM-DD`.
- Повертає масив об’єктів day/revenue/orders.

