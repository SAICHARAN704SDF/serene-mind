-- Serenemind Database Schema

-- Song table
CREATE TABLE song (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    artist VARCHAR(100) NOT NULL,
    url VARCHAR(200) NOT NULL
);

-- JournalEntry table
CREATE TABLE journal_entry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- MoodLog table
CREATE TABLE mood_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mood ENUM('ecstatic', 'happy', 'neutral', 'sad', 'awful') NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Patient table
CREATE TABLE patient (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dob VARCHAR(20) NOT NULL,
    contact VARCHAR(100) NOT NULL,
    medical_history TEXT NOT NULL
);

-- Doctor table
CREATE TABLE doctor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    contact VARCHAR(100) NOT NULL,
    license_number VARCHAR(50) NOT NULL,
    experience TEXT NOT NULL
);

-- Appointment table
CREATE TABLE appointment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    date VARCHAR(20) NOT NULL,
    time VARCHAR(20) NOT NULL,
    purpose TEXT NOT NULL,
    status ENUM('scheduled', 'completed', 'canceled') DEFAULT 'scheduled',
    FOREIGN KEY (patient_id) REFERENCES patient(id),
    FOREIGN KEY (doctor_id) REFERENCES doctor(id)
);

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