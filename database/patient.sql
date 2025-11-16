-- Patient table
CREATE TABLE patient (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dob VARCHAR(20) NOT NULL,
    contact VARCHAR(100) NOT NULL,
    medical_history TEXT NOT NULL
);