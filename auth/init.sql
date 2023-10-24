CREATE USER "auth_user"@"mp3converter.com" IDENTIFIED BY "Auth123";

CREATE DATABASE auth;

GRANT ALL PRIVILEGES ON auth.* TO "auth_user"@"mp3converter.com";

USE auth;

CREATE TABLE user (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

INSERT INTO user (email, password) VALUES ("user@gmail.com", "Admin123")
