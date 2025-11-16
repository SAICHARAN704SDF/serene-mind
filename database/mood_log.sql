-- MoodLog table
CREATE TABLE mood_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mood ENUM('ecstatic', 'happy', 'neutral', 'sad', 'awful') NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);