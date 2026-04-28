-- ============================================================
--  ParkSmart  –  Parking Management System
--  Database : parksmart
--  Run this file in MySQL Workbench / CLI to set up the DB
--
--  mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS parksmart
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE parksmart;

-- ============================================================
-- DDL : Table Definitions
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id       INT           AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(100)  NOT NULL,
    email    VARCHAR(100)  NOT NULL UNIQUE,
    phone    VARCHAR(15),
    password VARCHAR(100)  NOT NULL
);

CREATE TABLE IF NOT EXISTS parking_slots (
    id     INT                      AUTO_INCREMENT PRIMARY KEY,
    floor  INT                      NOT NULL,
    type   ENUM('Car','Bike')       NOT NULL,
    status ENUM('Available','Occupied') NOT NULL DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS bookings (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT,
    vehicle      VARCHAR(20)           NOT NULL,
    vehicle_type ENUM('Car','Bike')    NOT NULL,
    slot_id      INT,
    entry_time   DATETIME              NOT NULL DEFAULT CURRENT_TIMESTAMP,
    exit_time    DATETIME              NULL,
    total_fee    DECIMAL(10,2)         NOT NULL DEFAULT 0.00,
    status       ENUM('Active','Completed') NOT NULL DEFAULT 'Active',
    FOREIGN KEY (user_id) REFERENCES users(id)         ON DELETE SET NULL,
    FOREIGN KEY (slot_id) REFERENCES parking_slots(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS payments (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    booking_id   INT,
    amount       DECIMAL(10,2)       NOT NULL DEFAULT 0.00,
    payment_date DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status       ENUM('Pending','Paid') NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

-- ============================================================
-- DML : Sample / Seed Data
-- ============================================================

INSERT INTO users (name, email, phone, password) VALUES
('Rahul Sharma', 'rahul@gmail.com', '9876543210', 'rahul@123'),
('Priya Mehta',  'priya@gmail.com', '9123456789', 'priya@456'),
('Amit Kumar',   'amit@gmail.com',  '9988776655', 'amit@789'),
('Admin User',   'admin@park.com',  '9000000000', 'admin@123');

INSERT INTO parking_slots (floor, type, status) VALUES
(1, 'Car',  'Available'),
(1, 'Bike', 'Available'),
(2, 'Car',  'Occupied'),
(2, 'Car',  'Available'),
(2, 'Bike', 'Available'),
(3, 'Car',  'Available'),
(3, 'Car',  'Occupied'),
(3, 'Bike', 'Available');

INSERT INTO bookings (user_id, vehicle, vehicle_type, slot_id, entry_time, exit_time, total_fee, status) VALUES
(1, 'TN01AB1234', 'Car',  3, '2026-02-01 09:00:00', '2026-02-01 11:00:00', 100.00, 'Completed'),
(2, 'TN02CD5678', 'Bike', 7, '2026-04-04 10:30:00',  NULL,                   0.00, 'Active'),
(3, 'TN03EF9012', 'Car',  3, '2026-02-03 08:15:00', '2026-02-03 10:45:00', 150.00, 'Completed');

INSERT INTO payments (booking_id, amount, payment_date, status) VALUES
(1, 100.00, '2026-02-01 11:10:00', 'Paid'),
(2,   0.00, '2026-04-04 10:35:00', 'Pending'),
(3, 150.00, '2026-02-03 10:50:00', 'Paid');

-- ============================================================
-- Useful DML queries you can run to test the system:
--
-- SELECT * FROM users;
-- SELECT * FROM parking_slots WHERE status = 'Available';
-- SELECT b.id, u.name, b.vehicle, ps.floor, b.status, p.status AS paid
--   FROM bookings b
--   JOIN users u         ON b.user_id = u.id
--   JOIN parking_slots ps ON b.slot_id  = ps.id
--   JOIN payments p      ON p.booking_id = b.id;
--
-- UPDATE parking_slots SET status = 'Available' WHERE id = 3;
-- DELETE FROM bookings WHERE id = 2;
-- ============================================================
