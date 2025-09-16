CREATE TYPE role_bookstore AS ENUM ('borrower', 'admin');
CREATE TYPE crud AS ENUM ('create', 'read', 'update', 'delete');
CREATE TYPE transaction_type AS ENUM ('borrow', 'return');

-- Table: users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    role role_bookstore NOT NULL,
    password VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    phone_number VARCHAR NOT NULL
);

-- Table: permissions
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    permission_name VARCHAR,
    permission_type crud,
    description TEXT
);

-- Table: role_permission
CREATE TABLE role_permission (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_id INT NOT NULL REFERENCES permissions(id) ON DELETE CASCADE
);

-- Table: books
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    price_per_day INT NOT NULL,
    added_at TIMESTAMP
);

-- Table: book_transactions
CREATE TABLE book_transactions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id INT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    transaction transaction_type NOT NULL,
    transaction_time TIMESTAMP NOT NULL,
    transaction_cost INT NOT NULL
);