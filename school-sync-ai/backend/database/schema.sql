CREATE TABLE upload_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(64) NOT NULL,
    admission_no VARCHAR(100) NOT NULL,
    student_name VARCHAR(255),
    class_name VARCHAR(50),
    gender VARCHAR(20),
    category VARCHAR(20),
    language VARCHAR(20),
    source_sheet VARCHAR(50),
    INDEX idx_session (session_id),
    INDEX idx_admission (admission_no),
    INDEX idx_session_admission (session_id, admission_no)
);

CREATE TABLE comparison_results (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(64) NOT NULL,
    admission_no VARCHAR(64) NOT NULL,
    difference_type VARCHAR(50) NOT NULL,
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    INDEX idx_comp_session (session_id)
);