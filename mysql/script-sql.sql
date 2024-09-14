CREATE DATABASE IF NOT EXISTS classifier_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE classifier_db;

-- Ajuste para agregar la columna database_name
CREATE TABLE IF NOT EXISTS database_connection (
    id INT AUTO_INCREMENT PRIMARY KEY,
    host VARCHAR(255) NOT NULL,
    port INT NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    database_name VARCHAR(255) -- Columna agregada
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS scan_result (
    id INT AUTO_INCREMENT PRIMARY KEY,
    database_id INT NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    column_name VARCHAR(255) NOT NULL,
    information_type VARCHAR(255),
    data_type VARCHAR(255),
    FOREIGN KEY (database_id) REFERENCES database_connection(id) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password VARCHAR(120) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user'
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
