CREATE DATABASE IF NOT EXISTS rubriq_africa;
USE rubriq_africa;


CREATE TABLE about_content (
	id INTEGER NOT NULL, 
	title VARCHAR(255), 
	hero_description TEXT, 
	background TEXT, 
	mission TEXT, 
	vision TEXT, 
	`values` TEXT, 
	image_url VARCHAR(500), 
	PRIMARY KEY (id)
)

;

CREATE TABLE contact_info (
	id INTEGER NOT NULL, 
	phone VARCHAR(50), 
	email VARCHAR(120), 
	location VARCHAR(255), 
	socials JSON, 
	PRIMARY KEY (id)
)

;

CREATE TABLE delivered_order_history (
	id INTEGER NOT NULL, 
	order_type VARCHAR(20), 
	customer_name VARCHAR(100), 
	phone VARCHAR(20), 
	address VARCHAR(255), 
	payment_method VARCHAR(50), 
	message TEXT, 
	product_snapshot TEXT, 
	status VARCHAR(20), 
	created_at DATETIME, 
	month INTEGER, 
	year INTEGER, 
	PRIMARY KEY (id)
)

;

CREATE TABLE inquiries (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	message TEXT NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id)
)

;

CREATE TABLE monthly_sales_performance (
	id INTEGER NOT NULL, 
	year INTEGER NOT NULL, 
	month INTEGER NOT NULL, 
	total_delivered_orders INTEGER, 
	last_updated DATETIME, 
	rejected_orders INTEGER, 
	PRIMARY KEY (id), 
	CONSTRAINT unique_month_year UNIQUE (year, month)
)

;

CREATE TABLE monthly_top_product (
	id INTEGER NOT NULL, 
	year INTEGER NOT NULL, 
	month INTEGER NOT NULL, 
	product_name VARCHAR(255) NOT NULL, 
	total_quantity INTEGER, 
	PRIMARY KEY (id)
)

;

CREATE TABLE `pageViewers` (
	id INTEGER NOT NULL, 
	timestamp DATETIME, 
	PRIMARY KEY (id)
)

;

CREATE TABLE products (
	id INTEGER NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	description TEXT NOT NULL, 
	category VARCHAR(50) NOT NULL, 
	price FLOAT NOT NULL, 
	unit VARCHAR(50), 
	stock INTEGER, 
	image VARCHAR(255), 
	PRIMARY KEY (id)
)

;

CREATE TABLE questions (
	id INTEGER NOT NULL, 
	title VARCHAR(255), 
	faqs JSON, 
	PRIMARY KEY (id)
)

;

CREATE TABLE user_otps (
	id INTEGER NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	otp_code INTEGER NOT NULL, 
	expiry DATETIME NOT NULL, 
	attempts INTEGER, 
	PRIMARY KEY (id)
)

;

CREATE TABLE users (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	email VARCHAR(120), 
	phone VARCHAR(20) NOT NULL, 
	password VARCHAR(255) NOT NULL, 
	profile_image VARCHAR(500), 
	address VARCHAR(255), 
	bio TEXT, 
	is_admin BOOLEAN, 
	role VARCHAR(20), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (email), 
	UNIQUE (phone)
)

;

CREATE TABLE carts (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	product_name VARCHAR(255) NOT NULL, 
	product_image VARCHAR(500), 
	product_price FLOAT NOT NULL, 
	quantity INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
)

;

CREATE TABLE messages (
	id INTEGER NOT NULL, 
	name VARCHAR(120), 
	phone VARCHAR(20), 
	subject VARCHAR(200), 
	message TEXT, 
	created_at DATETIME, 
	is_delivered BOOLEAN, 
	is_rejected BOOLEAN, 
	customer_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES users (id)
)

;

CREATE TABLE orders (
	id INTEGER NOT NULL, 
	customer_name VARCHAR(100) NOT NULL, 
	phone VARCHAR(20) NOT NULL, 
	address VARCHAR(200) NOT NULL, 
	street_number VARCHAR(50), 
	payment_method VARCHAR(50), 
	message TEXT, 
	created_at DATETIME, 
	order_status VARCHAR(20), 
	is_rejected BOOLEAN, 
	customer_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES users (id)
)

;

CREATE TABLE cart_items (
	id INTEGER NOT NULL, 
	cart_id INTEGER, 
	product_id INTEGER, 
	quantity INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(cart_id) REFERENCES carts (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
)

;

CREATE TABLE order_items (
	id INTEGER NOT NULL, 
	order_id INTEGER NOT NULL, 
	product_id INTEGER, 
	product_name VARCHAR(100), 
	image VARCHAR(255), 
	quantity INTEGER, 
	product_type VARCHAR(20), 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES orders (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
)

;
