-- Active: 1782680027282@@localhost@5332@retail@public
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

CREATE TABLE IF NOT EXISTS regions (
    region_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    name VARCHAR(100) UNIQUE NOT NULL
);


CREATE TABLE IF NOT EXISTS category (
    category_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    category_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS customer (
    customer_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    first_name VARCHAR(255) NOT NULL , 
    last_name VARCHAR(255) NOT NULL , 
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL, 
    address VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS branch (
    branch_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    region_id INT REFERENCES regions(region_id) NOT NULL
);


CREATE TABLE IF NOT EXISTS  product (
    product_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id INT REFERENCES category(category_id) NOT NULL, 
    name VARCHAR(255) UNIQUE NOT NULL ,
    price DECIMAL(10,2) NOT NULL CHECK(price > 0)
);


CREATE TABLE IF NOT EXISTS  employee (
    employee_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    branch_id INT REFERENCES branch(branch_id) ON DELETE SET NULL 
);


CREATE TABLE IF NOT EXISTS orders(
    order_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INT REFERENCES customer(customer_id) NOT NULL,
    order_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    branch_id INT REFERENCES branch(branch_id) NOT NULL,
    employee_id INT REFERENCES employee(employee_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS order_items(
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE NOT NULL,
    product_id INT REFERENCES product(product_id) NOT NULL,
    quantity INT NOT NULL CHECK(quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK(unit_price > 0), 
    PRIMARY KEY (order_id , product_id)
);

