CREATE SCHEMA dw;

CREATE TABLE dw.dim_time (
    date_key INT PRIMARY KEY NOT NULL,
    full_date DATE NOT NULL, 
    week SMALLINT NOT NULL, 
    month SMALLINT NOT NULL,
    year SMALLINT  NOT NULL , 
    quarter SMALLINT NOT NULL
)

CREATE TABLE dw.dim_product (
    product_key INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY , 
    product_id INT NOT NULL, 
    category_id INT NOT NULL,
    category_name VARCHAR(256) NOT NULL,
    name VARCHAR(256) NOT NULL,
    price DECIMAL(10,2) check (price > 0) NOT NULL,
    valid_from DATE NOT NULL , 
    valid_to DATE DEFAULT NULL,
    is_current BOOLEAN DEFAULT TRUE
)

CREATE TABLE dw.dim_branch (
    branch_key INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY ,
    branch_id INT NOT NULL,
    city VARCHAR(256) NOT NULL,
    region_id INT NOT NULL,
    region_name VARCHAR(256) NOT NULL 
)

CREATE TABLE dw.dim_customer (
    customer_key  INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    customer_id INT NOT NULL,
    first_name VARCHAR(255) NOT NULL , 
    last_name VARCHAR(255) NOT NULL , 
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(100) NOT NULL, 
    address VARCHAR(255)
)


CREATE TABLE dw.dim_employee (
    employee_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id INT NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(100)  NOT NULL
);

CREATE TABLE dw.fact_retail (
    fact_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_key INT NOT NULL REFERENCES dw.dim_time(date_key),
    product_key INT NOT NULL REFERENCES dw.dim_product(product_key),
    branch_key INT NOT NULL REFERENCES dw.dim_branch(branch_key),
    customer_key INT NOT NULL REFERENCES dw.dim_customer(customer_key),
    employee_key INT REFERENCES dw.dim_employee(employee_key),
    order_id INT not NULL, 
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    line_total DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);