-- Doctor table
CREATE TABLE doctor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    contact VARCHAR(100) NOT NULL,
    license_number VARCHAR(50) NOT NULL,
    experience TEXT NOT NULL
);