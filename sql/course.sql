-- SQL file with table with tracker output
CREATE TABLE Course (
    ID INT PRIMARY KEY,
    Title VARCHAR2(255) UNIQUE,
    URL VARCHAR2(255) UNIQUE,
    Description VARCHAR2(255)
);
