DROP DATABASE IF EXISTS smart_library;
CREATE DATABASE smart_library;
USE smart_library;
CREATE TABLE shelves (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    shelf_code VARCHAR(20) NOT NULL UNIQUE,
    shelf_name VARCHAR(50) NOT NULL,
    category   VARCHAR(20) NOT NULL,
    floor      INT NOT NULL DEFAULT 1,
    map_x      FLOAT NOT NULL DEFAULT 0,
    map_y      FLOAT NOT NULL DEFAULT 0
);

CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE books (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    rfid_tag          VARCHAR(50) NOT NULL UNIQUE,
    title             VARCHAR(200) NOT NULL,
    author            VARCHAR(150),
    isbn              VARCHAR(20),
    category          VARCHAR(50),
    expected_shelf_id INT NOT NULL,
    current_shelf_id  INT NULL,
    status            ENUM('on shelf','borrowed','misplaced') NOT NULL DEFAULT 'on shelf',
    FOREIGN KEY (expected_shelf_id) REFERENCES shelves(id),
    FOREIGN KEY (current_shelf_id) REFERENCES shelves(id)
);

CREATE TABLE scan_logs (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    book_id      INT NOT NULL,
    shelf_id     INT NOT NULL,
    scanned_by   INT NULL,
    scanned_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_misplaced BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (shelf_id) REFERENCES shelves(id),
    FOREIGN KEY (scanned_by) REFERENCES users(id)
);

CREATE TABLE students (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    university_id   VARCHAR(20) NOT NULL UNIQUE,
    student_name    VARCHAR(150) NOT NULL,
    enrollment_year INT,
    department_code VARCHAR(10)
);

CREATE TABLE borrowings (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    book_id     INT NOT NULL,
    student_id  INT NOT NULL,
    borrowed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date    DATE NOT NULL,
    returned_at DATETIME NULL,
    status      ENUM('active','returned','overdue') NOT NULL DEFAULT 'active',
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- SHELVES -- ********************************************************************************* 
INSERT INTO shelves (shelf_code, shelf_name, category, floor, map_x, map_y) VALUES
('A', 'Shelf A', 'Science', 1, 120, 200),
('B', 'Shelf B', 'Literature', 1, 280, 200),
('C', 'Shelf C', 'Engineering', 1, 440, 200),
('D', 'Shelf D', 'History', 1, 600, 200);

-- USERS -- *********************************************************************************
INSERT INTO users (username, password_hash) VALUES
('admin', 'placeholder_hash_will_be_replaced_by_flask'),
('librarian1', 'placeholder_hash_will_be_replaced_by_flask');

-- BOOKS -- *********************************************************************************

-- Shelf A, Science (id = 1)
INSERT INTO books (rfid_tag, title, author, isbn, category, expected_shelf_id, current_shelf_id, status) VALUES
('E2:45:A1:3F', 'Physics', 'Jim Al-Khalili', '978-0199572854', 'Science', 1, 1, 'on shelf'),
('F3:82:B7:1D', 'Introduction to Quantum Mechanics', 'David Griffiths', '978-1107189638', 'Science', 1, 1, 'on shelf'),
('A1:19:C4:8E', 'Calculus: Early Transcendentals', 'James Stewart', '978-1285741550', 'Science', 1, 1, 'on shelf'),
('B7:56:D2:9A', 'Chemistry', 'Steven Zumdahl', '978-1305957404', 'Science', 1, 3, 'misplaced'),
('C8:23:E5:4B', 'Thermodynamics: An Engineering Approach', 'Yunus Cengel', '978-0073398174', 'Science', 1, 1, 'on shelf');

-- Shelf B, Literature (id = 2)
INSERT INTO books (rfid_tag, title, author, isbn, category, expected_shelf_id, current_shelf_id, status) VALUES
('D4:67:F8:2C', 'The Complete Works of Shakespeare', 'William Shakespeare', '978-0141396217', 'Literature', 2, 2, 'on shelf'),
('E9:34:A2:7D', 'Hamlet', 'William Shakespeare', '978-0743477123', 'Literature', 2, 2, 'on shelf'),
('F1:78:B3:9E', 'Palace Walk', 'Naguib Mahfouz', '978-0385264662', 'Literature', 2, 2, 'on shelf'),
('A5:12:C6:3F', 'The Prophet', 'Gibran Khalil Gibran', '978-0394404288', 'Literature', 2, 4, 'misplaced'),
('B2:89:D4:1A', 'The Days', 'Taha Hussein', '978-9774248009', 'Literature', 2, 2, 'on shelf'),
('C6:45:E7:8B', 'Men in the Sun', 'Ghassan Kanafani', '978-0894108570', 'Literature', 2, 2, 'on shelf'),
('D3:90:F1:5C', 'Season of Migration to the North', 'Tayeb Salih', '978-1590173022', 'Literature', 2, 2, 'on shelf');

-- Shelf C, Engineering (id = 3)
INSERT INTO books (rfid_tag, title, author, isbn, category, expected_shelf_id, current_shelf_id, status) VALUES
('E7:56:A8:2D', 'Introduction to Algorithms', 'Thomas Cormen', '978-0262033848', 'Engineering', 3, 3, 'on shelf'),
('F8:23:B9:4E', 'Algorithms', 'Robert Sedgewick', '978-0321573513', 'Engineering', 3, 3, 'on shelf'),
('A3:67:C1:7F', 'Digital Design', 'Morris Mano', '978-0132774208', 'Engineering', 3, 3, 'on shelf'),
('B9:12:D5:8A', 'Computer Organization and Architecture', 'William Stallings', '978-0134997193', 'Engineering', 3, 1, 'misplaced'),
('C4:78:E2:3B', 'Signals and Systems', 'Alan Oppenheim', '978-0138147570', 'Engineering', 3, 3, 'on shelf'),
('D1:34:F6:9C', 'Information Security: Principles and Practice', 'Mark Stamp', '978-1119505907', 'Engineering', 3, 3, 'on shelf'),
('E5:90:A7:4D', 'Software Engineering', 'Ian Sommerville', '978-0137035151', 'Engineering', 3, 3, 'on shelf'),
('F2:45:B8:6E', 'Computers as Components', 'Marilyn Wolf', '978-0128053874', 'Engineering', 3, 3, 'on shelf'),
('A8:67:C3:9F', 'Data and Computer Communications', 'William Stallings', '978-0132392049', 'Engineering', 3, 3, 'on shelf');

-- Shelf D, History (id = 4)
INSERT INTO books (rfid_tag, title, author, isbn, category, expected_shelf_id, current_shelf_id, status) VALUES
('B4:12:D9:2A', 'World Civilizations: The Global Experience', 'Peter Stearns', '978-0134056838', 'History', 4, 4, 'on shelf'),
('C9:78:E1:5B', 'Science and Technology in Islam', 'Ahmad Al-Hassan', '978-9231027529', 'History', 4, 4, 'on shelf'),
('D6:34:F4:8C', 'A History of the Arab Peoples', 'Albert Hourani', '978-0571288014', 'History', 4, 4, 'on shelf'),
('E3:90:A5:1D', 'Osmans Dream: History of the Ottoman Empire', 'Caroline Finkel', '978-0465023967', 'History', 4, 4, 'on shelf');

-- One book currently borrowed (no current shelf)
INSERT INTO books (rfid_tag, title, author, isbn, category, expected_shelf_id, current_shelf_id, status) VALUES
('F7:45:B2:4E', 'Linear Algebra and Its Applications', 'David Lay', '978-0321982384', 'Science', 1, NULL, 'borrowed');

-- STUDENTS -- *********************************************************************************
INSERT INTO students (university_id, student_name, enrollment_year, department_code) VALUES
('DEMO001', 'Demo Student One', 2022, 'CE'),
('DEMO002', 'Demo Student Two', 2022, 'CE'),
('DEMO003', 'Demo Student Three', 2022, 'CE'),
('DEMO004', 'Demo Student Four', 2023, 'CS'),
('DEMO005', 'Demo Student Five', 2021, 'EE'),
('DEMO006', 'Demo Student Six', 2023, 'CE');

-- SCAN LOGS -- ********************************************************************************* 
INSERT INTO scan_logs (book_id, shelf_id, scanned_by, scanned_at, is_misplaced) VALUES
-- Scanning Shelf A
(1,  1, 1, '2026-06-25 09:15:00', FALSE),  -- Physics on Shelf A — correct
(2,  1, 1, '2026-06-25 09:15:30', FALSE),  -- Quantum Mech on Shelf A — correct
(3,  1, 1, '2026-06-25 09:16:00', FALSE),  -- Calculus on Shelf A — correct
-- Scanning Shelf B
(6,  2, 1, '2026-06-25 09:30:00', FALSE),  -- Shakespeare on Shelf B — correct
(7,  2, 1, '2026-06-25 09:30:30', FALSE),  -- Hamlet on Shelf B — correct
-- Scanning Shelf C
(12, 3, 1, '2026-06-25 10:00:00', FALSE),  -- Algorithms on Shelf C — correct
(4,  3, 1, '2026-06-25 10:01:00', TRUE),   -- Chemistry found on Shelf C — MISPLACED (should be A)
(16, 1, 1, '2026-06-25 10:15:00', TRUE),   -- Stallings found on Shelf A — MISPLACED (should be C)
-- Scanning Shelf D
(22, 4, 1, '2026-06-25 10:30:00', FALSE),  -- World Civilizations on Shelf D — correct
(9,  4, 1, '2026-06-25 10:31:00', TRUE);   -- The Prophet found on Shelf D — MISPLACED (should be B)

-- BORROWINGS -- *********************************************************************************

INSERT INTO borrowings (book_id, student_id, borrowed_at, due_date, returned_at, status) VALUES
-- Deyaa has Linear Algebra currently borrowed
(26, 1, '2026-06-28 14:00:00', '2026-07-12', NULL, 'active'),
-- Demo Student Two returned a book
(1, 2, '2026-06-10 10:00:00', '2026-06-24', '2026-06-22 11:30:00', 'returned'),
-- Demo Student Four returned a book
(12, 4, '2026-06-15 09:00:00', '2026-06-29', '2026-06-28 16:00:00', 'returned'),
-- Omar has an overdue book
(6, 5, '2026-06-01 11:00:00', '2026-06-15', NULL, 'overdue');

