-- Hospital Patient Queue Management System
-- MySQL Database Schema for XAMPP
-- Run this file in phpMyAdmin or MySQL command line

-- Create database (uncomment if needed)
-- CREATE DATABASE IF NOT EXISTS hospital_queue;
-- USE hospital_queue;

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token_no VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    symptoms TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Waiting',
    time_in DATETIME NOT NULL,
    time_out DATETIME NULL,
    INDEX idx_status (status),
    INDEX idx_department (department),
    INDEX idx_time_in (time_in)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default doctor user
-- Password: doctor123
INSERT INTO users (username, password, role) 
VALUES ('doctor', 'doctor123', 'doctor')
ON DUPLICATE KEY UPDATE username=username;

-- Sample data (optional - uncomment if you want test data)
-- INSERT INTO patients (token_no, name, department, symptoms, status, time_in) VALUES
-- ('CARDIO-001', 'John Doe', 'Cardiology', 'Chest pain and shortness of breath', 'Waiting', NOW()),
-- ('ORTHO-001', 'Jane Smith', 'Orthopedics', 'Knee pain after fall', 'Waiting', NOW()),
-- ('NEURO-001', 'Bob Johnson', 'Neurology', 'Persistent headaches', 'In Consultation', NOW());


