-- BillingRecord table
CREATE TABLE billing_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    patient_id INT NOT NULL,
    service_description VARCHAR(200) NOT NULL,
    amount FLOAT NOT NULL,
    payment_status ENUM('pending', 'paid', 'overdue') DEFAULT 'pending',
    due_date VARCHAR(20) NOT NULL,
    notes TEXT,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointment(id),
    FOREIGN KEY (patient_id) REFERENCES patient(id)
);