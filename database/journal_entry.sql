-- JournalEntry table
CREATE TABLE journal_entry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);