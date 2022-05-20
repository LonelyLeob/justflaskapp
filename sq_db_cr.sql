CREATE TABLE IF NOT EXISTS works (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    desc VARCHAR(150),
    category_n integer
    FOREIGN KEY (category_n) REFERENCES category(id)
);

CREATE TABLE IF NOT EXISTS category (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    title TEXT
)

CREATE TABLE IF NOT EXISTS users (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    uname VARCHAR(50) NOT NULL,
    email TEXT NOT NULL UNIQUE,
    pwd STRING NOT NULL,
    photo BLOB DEFAULT NULL
);