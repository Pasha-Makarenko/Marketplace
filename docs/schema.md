Огляд схеми
===========

Сутності та зв’язки
-------------------
- `users` — облікові записи. FK-цілі для `sessions`, `orders`, `seller_profiles`, `ratings`, `reviews`.
- `sessions` — сесії автентифікації (для користувачів).
- `seller_profiles` — один-до-одного з `users` (унікальний user_id). Продавці володіють товарами.
- `categories` — ієрархічні через nullable `parent_category_id`.
- `products` — належать категоріям і продавцям; містять цінові/складські поля.
- `orders` — оформлюють користувачі; містять стан оплати/доставки; мають `order_items`.
- `order_items` — позиції замовлення (знімок даних товару).
- `ratings` — значення 1–5 для зв’язки user/product.
- `reviews` — текстові відгуки user/product.

Таблиці (ключові колонки)
-------------------------
### users
- `user_id` PK
- `email` (unique), `password_hash`
- `first_name`, `last_name`, `phone`
- `created_at`

### sessions
- `session_id` PK, `user_id` FK → users, `token`, `created_at`, `expires_at`

### seller_profiles
- `seller_id` PK
- `user_id` FK → users (unique)
- `store_name`, `store_logs`, `contact_info`, `return_policy`, `delivery_terms`
- `is_active`, `created_at`

### categories
- `category_id` PK
- `name`
- `parent_category_id` FK → categories (self), nullable, check проти самопосилання

### products
- `product_id` PK
- `name`, `description`, `price`, `discount`, `stock_quantity`
- `owner_id` FK → seller_profiles
- `category_id` FK → categories
- `created_at`, `updated_at`, `is_active`
- перевірки: name не порожнє, price ≥ 0, discount 0–100, stock_quantity ≥ 0

### orders
- `order_id` PK, `user_id` FK → users
- `status` (draft/pending/completed/cancelled)
- `payment_status`, `transaction_id`, `paid_at`
- `delivery_status`, `tracking_number`, `delivery_address`, `delivered_at`
- `created_at`, `updated_at`

### order_items
- складовий PK (`order_id`, `product_id`)
- `title`, `quantity`, `price_at_purchase`
- FK `order_id` → orders (cascade delete)

### ratings
- `rating_id` PK
- `user_id` FK → users
- `product_id` FK → products
- `value` (1–5, check), `created_at`

### reviews
- `review_id` PK
- `author_id` FK → users
- `product_id` FK → products
- `text`, `created_at`

Індекси та обмеження
--------------------
- Унікальні: `users.email`, `seller_profiles.user_id`
- Зовнішні ключі як описано; каскадні видалення для `order_items` тощо.
- Check-обмеження: categories (без самопосилання), products (price/discount/stock), ratings (1–5).

Нотатки щодо ORM
----------------
- Ідентифікатори мапляться через SQLAlchemy composites на value-object `Identity`.
- Колонки, що конфліктують за іменами, виключені через `exclude_properties`.

