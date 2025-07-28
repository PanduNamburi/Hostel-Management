-- Create the database
CREATE DATABASE IF NOT EXISTS hostel_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create the user and grant privileges
CREATE USER IF NOT EXISTS 'hostel_management'@'localhost' IDENTIFIED BY 'sIDDUT1@';
GRANT ALL PRIVILEGES ON hostel_management.* TO 'hostel_management'@'localhost';
FLUSH PRIVILEGES;

-- Show the created database and user
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User = 'hostel_management'; 