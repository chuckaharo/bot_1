-- Создание таблицы продуктов
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price_btc NUMERIC(16,8),
    price_ltc NUMERIC(16,8),
    file_id VARCHAR(255),
    stock INTEGER DEFAULT 0
);

-- Создание таблицы транзакций
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER REFERENCES products(id),
    crypto_address VARCHAR(255),
    amount NUMERIC(16,8),
    currency VARCHAR(10),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);

-- Права для пользователя БД
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO botuser;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO botuser;