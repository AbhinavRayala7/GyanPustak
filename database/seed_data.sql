-- =========================================================================
-- Project: Gyan Pustak - Library & Marketplace Database
-- Script: Seed Data Injection for SQLite (Auto-initialized on startup)
-- Password for all seeded users: password123
-- Hash generated using Werkzeug's default scrypt algorithm
-- =========================================================================

-- 1. Seed Users (SuperAdmin, Admin, Student)
INSERT INTO Users (Username, Email, PasswordHash, Phone, CollegeName, UserStatus, Role) VALUES
('superadmin', 'superadmin@gyanpustak.in', 'scrypt:32768:8:1$Sv60Vu5rlyC6WW2l$bc96f6f39dfeafe4ae0b6c27c74c966411b19cf6689c3289f80ac0951236fb17daab27aded2768765eb9ad72cddb86d4560642548a2ba5160cbe34726b477787', '9999999999', 'IIT Bhubaneswar', 'Active', 'SuperAdmin'),
('admin', 'admin@gyanpustak.in', 'scrypt:32768:8:1$Sv60Vu5rlyC6WW2l$bc96f6f39dfeafe4ae0b6c27c74c966411b19cf6689c3289f80ac0951236fb17daab27aded2768765eb9ad72cddb86d4560642548a2ba5160cbe34726b477787', '7013233579', 'IIT Bhubaneswar', 'Active', 'Admin'),
('abhinav', 'abhinav@gyanpustak.in', 'scrypt:32768:8:1$Sv60Vu5rlyC6WW2l$bc96f6f39dfeafe4ae0b6c27c74c966411b19cf6689c3289f80ac0951236fb17daab27aded2768765eb9ad72cddb86d4560642548a2ba5160cbe34726b477787', '8328631380', 'IIT Bhubaneswar', 'Active', 'Student'),
('user1', 'user1@gyanpustak.in', 'scrypt:32768:8:1$dlVLVmPajEpI94J4$16f36368b83b66448b7a3a4dc529c6e7da0aebe3444dac6e2ae3c96a304798f086e4910e969ba4f20ad3c8c27952d9c4ae84daa842a2d4847267a0affbb61549', '9876543210', 'Demo College', 'Active', 'Student'),
('student_rahul', 'rahul@gyanpustak.in', 'scrypt:32768:8:1$Sv60Vu5rlyC6WW2l$bc96f6f39dfeafe4ae0b6c27c74c966411b19cf6689c3289f80ac0951236fb17daab27aded2768765eb9ad72cddb86d4560642548a2ba5160cbe34726b477787', '9876543210', 'IIT Hyderabad', 'Active', 'Student'),
('student_sneha', 'sneha@gyanpustak.in', 'scrypt:32768:8:1$Sv60Vu5rlyC6WW2l$bc96f6f39dfeafe4ae0b6c27c74c966411b19cf6689c3289f80ac0951236fb17daab27aded2768765eb9ad72cddb86d4560642548a2ba5160cbe34726b477787', '9123456789', 'IIT Hyderabad', 'Active', 'Student'),
('student_locked', 'locked@gyanpustak.in', 'scrypt:32768:8:1$Sv60Vu5rlyC6WW2l$bc96f6f39dfeafe4ae0b6c27c74c966411b19cf6689c3289f80ac0951236fb17daab27aded2768765eb9ad72cddb86d4560642548a2ba5160cbe34726b477787', '0000000000', 'IIT Kharagpur', 'Suspended', 'Student');

-- 2. Seed Categories
INSERT INTO Categories (CategoryName, Description) VALUES
('Computer Science', 'Algorithms, Data Structures, Web Development, and Systems'),
('Electrical Engineering', 'Microelectronics, Signals and Systems, and Control Systems'),
('Mathematics', 'Calculus, Linear Algebra, and Probability'),
('Physics', 'Quantum Mechanics, Electrodynamics, and Optics');

-- 3. Seed Books
INSERT INTO Books (ISBN, Title, Author, Edition, Publisher, PublicationYear, CategoryID, TotalCopies, AvailableCopies) VALUES
('9780262033848', 'Introduction to Algorithms', 'Thomas H. Cormen', '3rd', 'MIT Press', 2009, 1, 5, 4),
('9780073523323', 'Database System Concepts', 'Abraham Silberschatz', '6th', 'McGraw-Hill', 2010, 1, 3, 3),
('9780132126953', 'Computer Networks', 'Andrew S. Tanenbaum', '5th', 'Pearson', 2010, 1, 4, 3),
('9780138147570', 'Signals and Systems', 'Alan V. Oppenheim', '2nd', 'Prentice Hall', 1996, 2, 2, 1),
('9780199738519', 'Microelectronic Circuits', 'Adel S. Sedra', '6th', 'Oxford University Press', 2009, 2, 3, 2),
('9780538497817', 'Calculus: Early Transcendentals', 'James Stewart', '7th', 'Cengage Learning', 2011, 3, 4, 4);

-- 4. Seed Listings (Store Products for Bookstore)
INSERT INTO Listings (BookID, SellerID, Condition, Price, ListingDescription, Stock, ListingStatus) VALUES
(1, 2, 'Very Good', 750.00, 'Hardcover, minimal pencil marks in early chapters. Perfect for CS algorithms class.', 2, 'Active'),
(5, 2, 'Like New', 600.00, 'Sedra and Smith Microelectronics. Used for one semester, virtually brand new.', 1, 'Active'),
(2, 3, 'Good', 450.00, 'Database System Concepts. Some cover wear, clean pages.', 3, 'Active'),
(4, 3, 'Acceptable', 350.00, 'Signals & Systems. Wear on spine, fully readable.', 1, 'Active');

-- 5. Seed BorrowedBooks (Library Records)
INSERT INTO BorrowedBooks (UserID, BookID, BorrowDate, DueDate, ReturnDate, Status) VALUES
(3, 1, '2026-06-15 10:00:00', '2026-06-30 10:00:00', '2026-06-29 14:00:00', 'Returned'),
(3, 4, '2026-07-01 11:30:00', '2026-07-16 11:30:00', NULL, 'Approved'),
(4, 3, '2026-07-03 09:15:00', '2026-07-18 09:15:00', NULL, 'Approved'),
(5, 5, '2026-07-05 14:20:00', '2026-07-20 14:20:00', NULL, 'Pending');

-- 6. Seed SupportTickets
INSERT INTO SupportTickets (UserID, Subject, Category, Description, Status) VALUES
(3, 'Cannot return book online', 'Library', 'I returned the Algorithms book to the library desk today, but my dashboard still shows it as issued.', 'Resolved'),
(4, 'Defect in purchased book copy', 'Store', 'The database book listed as "Good" arrived with the last 10 pages torn. Can I request a partial refund or exchange?', 'Open');

-- 7. Seed TicketMessages
INSERT INTO TicketMessages (TicketID, SenderID, MessageText) VALUES
(1, 3, 'I returned the Algorithms book to the library desk today, but my dashboard still shows it as issued.'),
(1, 2, 'Hi Abhinav, I checked our manual logs and have updated the status to Returned. Sorry for the delay.'),
(1, 3, 'Thanks for resolving it quickly!'),
(2, 4, 'The database book listed as "Good" arrived with the last 10 pages torn. Can I request a partial refund or exchange?');
