CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NULL,
    role ENUM('Admin', 'Customer') NOT NULL DEFAULT 'Customer',
);


CREATE TABLE products2 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    old_price DECIMAL(10,2),
    stock INT DEFAULT 0,
    status ENUM('Active','Inactive') DEFAULT 'Active',
    badge VARCHAR(50),
    stars INT DEFAULT 0,
    reviews INT DEFAULT 0,
    img TEXT
);