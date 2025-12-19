Огляд схеми
===========

ERD
---
Діаграма не включена в репозиторій; зв’язки описані нижче для швидкої навігації.

Сутності та зв’язки (огляд)
--------------------------

- `users` — облікові записи. FK-цілі для `sessions`, `orders`, `seller_profiles`, `ratings`, `reviews`.
- `sessions` — сесії автентифікації (для користувачів).
- `seller_profiles` — один-до-одного з `users` (унікальний user_id). Продавці володіють товарами.
- `categories` — ієрархічні через nullable `parent_category_id`.
- `products` — належать категоріям і продавцям; містять цінові/складські поля.
- `orders` — оформлюють користувачі; містять стан оплати/доставки; мають `order_items`.
- `order_items` — позиції замовлення (знімок даних товару).
- `ratings` — значення 1–5 для зв’язки user/product.
- `reviews` — текстові відгуки user/product.

Опис таблиць
------------

### Таблиця: `users`

Призначення: зберігає облікові записи користувачів.

| Стовпець      | Тип          | Обмеження        | Опис                      |
|---------------|--------------|------------------|---------------------------|
| user_id       | SERIAL       | PRIMARY KEY      | Ідентифікатор користувача |
| email         | VARCHAR(255) | UNIQUE, NOT NULL | Email користувача         |
| password_hash | VARCHAR(255) | NOT NULL         | Хешований пароль          |
| first_name    | VARCHAR(255) | NULL             | Ім’я                      |
| last_name     | VARCHAR(255) | NULL             | Прізвище                  |
| phone         | VARCHAR(32)  | NULL             | Телефон                   |
| created_at    | TIMESTAMP    | DEFAULT NOW()    | Час створення             |

Індекси:

- Унікальний на `email` (пошук при логіні).

Зв’язки:

- 1‑до‑багатьох: `orders`, `sessions`, `ratings`, `reviews`.
- 1‑до‑1: `seller_profiles` (через уникальність user_id).

### Таблиця: `sessions`

Призначення: сесії автентифікації.

| Стовпець   | Тип       | Обмеження     | Опис                |
|------------|-----------|---------------|---------------------|
| session_id | SERIAL    | PRIMARY KEY   | Ідентифікатор сесії |
| user_id    | INTEGER   | FK → users    | Користувач          |
| token      | TEXT      | NOT NULL      | Сесійний токен      |
| created_at | TIMESTAMP | DEFAULT NOW() | Створена            |
| expires_at | TIMESTAMP | NOT NULL      | Час протермінування |

Зв’язки: Багато‑до‑1 → `users`.

### Таблиця: `seller_profiles`

Призначення: профілі продавців (1:1 з users).

| Стовпець       | Тип       | Обмеження             | Опис               |
|----------------|-----------|-----------------------|--------------------|
| seller_id      | SERIAL    | PRIMARY KEY           | Ідентифікатор      |
| user_id        | INTEGER   | FK → users, UNIQUE    | Користувач         |
| store_name     | VARCHAR   | NOT NULL              | Назва магазину     |
| store_logs     | VARCHAR   | NULL                  | Логи/опис          |
| contact_info   | TEXT      | NULL                  | Контакти           |
| return_policy  | TEXT      | NULL                  | Політика повернень |
| delivery_terms | TEXT      | NULL                  | Умови доставки     |
| is_active      | BOOLEAN   | NOT NULL DEFAULT true | Активність         |
| created_at     | TIMESTAMP | DEFAULT NOW()         | Створено           |

Зв’язки:

- 1‑до‑1 → `users` (унікальний user_id).
- 1‑до‑багатьох → `products`.

### Таблиця: `categories`

Призначення: довідник категорій з ієрархією.

| Стовпець           | Тип     | Обмеження                    | Опис                  |
|--------------------|---------|------------------------------|-----------------------|
| category_id        | SERIAL  | PRIMARY KEY                  | Ідентифікатор         |
| name               | VARCHAR | NOT NULL                     | Назва                 |
| parent_category_id | INTEGER | FK → categories, NULL, CHECK | Батьківська категорія |

Обмеження: `category_id <> parent_category_id` (запобігання самопосиланню).

Зв’язки: самопосилання (дерево), 1‑до‑багатьох з `products`.

### Таблиця: `products`

Призначення: товари.

| Стовпець       | Тип       | Обмеження                      | Опис          |
|----------------|-----------|--------------------------------|---------------|
| product_id     | SERIAL    | PRIMARY KEY                    | Ідентифікатор |
| name           | VARCHAR   | NOT NULL                       | Назва         |
| description    | TEXT      | NULL                           | Опис          |
| price          | NUMERIC   | NOT NULL, CHECK price ≥ 0      | Ціна          |
| discount       | INTEGER   | NOT NULL, CHECK 0–100          | Знижка %      |
| stock_quantity | INTEGER   | NOT NULL, CHECK ≥ 0            | Залишок       |
| owner_id       | INTEGER   | FK → seller_profiles           | Продавець     |
| category_id    | INTEGER   | FK → categories                | Категорія     |
| created_at     | TIMESTAMP | DEFAULT NOW()                  | Створено      |
| updated_at     | TIMESTAMP | DEFAULT NOW(), ON UPDATE NOW() | Оновлено      |
| is_active      | BOOLEAN   | NOT NULL DEFAULT true          | Активність    |

Зв’язки: багато‑до‑1 → `seller_profiles`, `categories`. 1‑до‑багатьох → `ratings`, `reviews`, `order_items`.

### Таблиця: `orders`

Призначення: замовлення користувачів.

| Стовпець         | Тип    | Обмеження                      | Опис                                 |
|------------------|--------|--------------------------------|--------------------------------------|
| order_id         | SERIAL | PK                             | Ідентифікатор                        |
| user_id          | INT    | FK → users                     | Покупець                             |
| status           | ENUM   | NOT NULL                       | Статус (draft/pending/completed/...) |
| payment_status   | ENUM   | NOT NULL                       | Статус оплати                        |
| transaction_id   | STRING | NULL                           | Ідентифікатор транзакції             |
| paid_at          | TS TZ  | NULL                           | Час оплати                           |
| delivery_status  | ENUM   | NOT NULL                       | Статус доставки                      |
| tracking_number  | STRING | NULL                           | Трекінг                              |
| delivery_address | STRING | NULL                           | Адреса доставки                      |
| delivered_at     | TS TZ  | NULL                           | Час доставки                         |
| created_at       | TS TZ  | DEFAULT NOW()                  | Створено                             |
| updated_at       | TS TZ  | DEFAULT NOW(), ON UPDATE NOW() | Оновлено                             |

Зв’язки: багато‑до‑1 → `users`; 1‑до‑багатьох → `order_items`.

### Таблиця: `order_items`

Призначення: позиції замовлення (знімок даних товару).

| Стовпець          | Тип     | Обмеження                                              | Опис                    |
|-------------------|---------|--------------------------------------------------------|-------------------------|
| order_id          | INTEGER | PK (разом з product_id), FK → orders ON DELETE CASCADE | Замовлення              |
| product_id        | INTEGER | PK (разом з order_id)                                  | Товар (ідентифікатор)   |
| title             | VARCHAR | NOT NULL                                               | Назва на момент купівлі |
| quantity          | INTEGER | NOT NULL                                               | Кількість               |
| price_at_purchase | NUMERIC | NOT NULL                                               | Ціна на момент купівлі  |

### Таблиця: `ratings`

Призначення: числові оцінки товарів.

| Стовпець   | Тип    | Обмеження           | Опис            |
|------------|--------|---------------------|-----------------|
| rating_id  | SERIAL | PK                  | Ідентифікатор   |
| user_id    | INT    | FK → users          | Автор оцінки    |
| product_id | INT    | FK → products       | Товар           |
| value      | INT    | NOT NULL, CHECK 1–5 | Значення оцінки |
| created_at | TS TZ  | DEFAULT NOW()       | Час створення   |

### Таблиця: `reviews`

Призначення: текстові відгуки.

| Стовпець   | Тип    | Обмеження     | Опис          |
|------------|--------|---------------|---------------|
| review_id  | SERIAL | PK            | Ідентифікатор |
| author_id  | INT    | FK → users    | Автор відгуку |
| product_id | INT    | FK → products | Товар         |
| text       | TEXT   | NULL          | Текст відгуку |
| created_at | TS TZ  | DEFAULT NOW() | Час створення |

Індекси та обмеження
--------------------

- Унікальні: `users.email`, `seller_profiles.user_id`.
- FK з каскадним видаленням для `order_items`; стандартні FK для інших таблиць.
- Check-обмеження: categories (без самопосилання), products (price/discount/stock), ratings (1–5).

Нотатки щодо ORM
----------------

- Ідентифікатори мапляться через SQLAlchemy composites на value-object `Identity`.
- Колонки, що конфліктують за іменами, виключені через `exclude_properties`.

Рішення щодо дизайну
--------------------

- Обрана 3НФ: довідники (`categories`, `seller_profiles`) відокремлені; дублювання лише в `order_items` як історичний знімок.
- Композити для ідентифікаторів у домені спрощують перевірки/порівняння та роботу з Value Object.
- Перевірки (CHECK) на ключових числових полях запобігають некоректним даним (price, discount, stock, rating).
- Ієрархія категорій через self-FK дає простіші запити для побудови дерева.
- Стратегія індексування: унікальні на логін (`email`), селектори на зовнішніх ключах (owner_id, category_id, user_id), індекси на часті фільтри (
  stock_quantity для low-stock, created_at для аналітики).

