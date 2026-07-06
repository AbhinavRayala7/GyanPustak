-- =========================================================================
-- Project: GyanPustak - College Textbook Marketplace Database
-- Script: Seed Data Injection
-- Target RDBMS: Microsoft SQL Server (T-SQL)
-- Description: Injects mock data representing realistic users, categories, 
--              books, listings, orders, order items, and reviews.
-- =========================================================================

-- USE GyanPustak;
-- GO

-- Disable foreign key check constraints temporarily if needed, but since we insert 
-- in correct dependency order, we don't need to disable constraints.

-- 1. Populate Categories
INSERT INTO dbo.Categories (CategoryName, Description) VALUES
(N'Computer Science', N'Books on Programming, Algorithms, Databases, Networks, and AI'),
(N'Electrical Engineering', N'Books on Circuits, Signal Processing, Microelectronics, and Power Systems'),
(N'Mathematics', N'Books on Calculus, Linear Algebra, Probability, and Discrete Math'),
(N'Mechanical Engineering', N'Books on Thermodynamics, Fluid Mechanics, CAD, and Robotics'),
(N'Physics', N'Books on Classical Mechanics, Electromagnetism, and Quantum Physics');
GO

-- 2. Populate Users (Buyers & Sellers from different IIT campuses)
INSERT INTO dbo.Users (Username, Email, PasswordHash, Phone, CollegeName, UserStatus) VALUES
(N'abhinav_r', N'abhinavrayala7@gmail.com', 'bcrypt_hash_1', '8328631380', N'IIT Bhubaneswar', 'Active'),
(N'prasanth_r', N'21ee01049@iitbbs.ac.in', 'bcrypt_hash_2', '7013233579', N'IIT Bhubaneswar', 'Active'),
(N'rahul_s', N'rahuls@iith.ac.in', 'bcrypt_hash_3', '9876543210', N'IIT Hyderabad', 'Active'),
(N'sneha_m', N'sneham@iith.ac.in', 'bcrypt_hash_4', '9123456789', N'IIT Hyderabad', 'Active'),
(N'amit_k', N'amitk@iitkgp.ac.in', 'bcrypt_hash_5', '9988776655', N'IIT Kharagpur', 'Active'),
(N'priya_d', N'priyad@iitbbs.ac.in', 'bcrypt_hash_6', '8877665544', N'IIT Bhubaneswar', 'Active'),
(N'vikram_g', N'vikramg@iith.ac.in', 'bcrypt_hash_7', '7766554433', N'IIT Hyderabad', 'Suspended');
GO

-- 3. Populate Books
-- Insert standard textbooks mapped to their categories
DECLARE @CS INT = (SELECT CategoryID FROM dbo.Categories WHERE CategoryName = N'Computer Science');
DECLARE @EE INT = (SELECT CategoryID FROM dbo.Categories WHERE CategoryName = N'Electrical Engineering');
DECLARE @MA INT = (SELECT CategoryID FROM dbo.Categories WHERE CategoryName = N'Mathematics');
DECLARE @PH INT = (SELECT CategoryID FROM dbo.Categories WHERE CategoryName = N'Physics');

INSERT INTO dbo.Books (ISBN, Title, Author, Edition, Publisher, PublicationYear, CategoryID) VALUES
('9780262033848', N'Introduction to Algorithms', N'Thomas H. Cormen', N'3rd', N'MIT Press', 2009, @CS),
('9780073523323', N'Database System Concepts', N'Abraham Silberschatz', N'6th', N'McGraw-Hill', 2010, @CS),
('9780132126953', N'Computer Networks', N'Andrew S. Tanenbaum', N'5th', N'Pearson', 2010, @CS),
('9780138147570', N'Signals and Systems', N'Alan V. Oppenheim', N'2nd', N'Prentice Hall', 1996, @EE),
('9780199738519', N'Microelectronic Circuits', N'Adel S. Sedra', N'6th', N'Oxford University Press', 2009, @EE),
('9780538497817', N'Calculus: Early Transcendentals', N'James Stewart', N'7th', N'Cengage Learning', 2011, @MA),
('9780321501219', N'Introduction to Electrodynamics', N'David J. Griffiths', N'4th', N'Pearson', 2012, @PH);
GO

-- 4. Populate Listings
-- Insert active and sold listings by users from different colleges
DECLARE @Abhinav INT = (SELECT UserID FROM dbo.Users WHERE Username = N'abhinav_r');
DECLARE @Prasanth INT = (SELECT UserID FROM dbo.Users WHERE Username = N'prasanth_r');
DECLARE @Rahul INT = (SELECT UserID FROM dbo.Users WHERE Username = N'rahul_s');
DECLARE @Sneha INT = (SELECT UserID FROM dbo.Users WHERE Username = N'sneha_m');
DECLARE @Amit INT = (SELECT UserID FROM dbo.Users WHERE Username = N'amit_k');

DECLARE @Algo INT = (SELECT BookID FROM dbo.Books WHERE ISBN = '9780262033848');
DECLARE @DB INT = (SELECT BookID FROM dbo.Books WHERE ISBN = '9780073523323');
DECLARE @Net INT = (SELECT BookID FROM dbo.Books WHERE ISBN = '9780132126953');
DECLARE @Sig INT = (SELECT BookID FROM dbo.Books WHERE ISBN = '9780138147570');
DECLARE @Micro INT = (SELECT BookID FROM dbo.Books WHERE ISBN = '9780199738519');
DECLARE @Calc INT = (SELECT BookID FROM dbo.Books WHERE ISBN = '9780538497817');

-- Active Listings
INSERT INTO dbo.Listings (SellerID, BookID, Condition, Price, ListingDescription, DateListed, ListingStatus) VALUES
(@Abhinav, @Algo, N'Very Good', 750.00, N'Minimal highlights. Useful for algorithms class.', DATEADD(day, -10, SYSDATETIME()), 'Active'),
(@Prasanth, @Micro, N'Like New', 600.00, N'Barely used Sedra & Smith. No tears.', DATEADD(day, -8, SYSDATETIME()), 'Active'),
(@Rahul, @Algo, N'Good', 680.00, N'Some corner wear but pages are neat.', DATEADD(day, -5, SYSDATETIME()), 'Active'),
(@Sneha, @DB, N'Acceptable', 450.00, N'Cover is taped but fully readable.', DATEADD(day, -3, SYSDATETIME()), 'Active'),
(@Amit, @Calc, N'New', 900.00, N'Brand new. Ordered by mistake.', DATEADD(day, -2, SYSDATETIME()), 'Active');

-- Sold / Reserved Listings
INSERT INTO dbo.Listings (SellerID, BookID, Condition, Price, ListingDescription, DateListed, ListingStatus) VALUES
(@Prasanth, @Algo, N'Like New', 800.00, N'Like new, no markings.', DATEADD(day, -15, SYSDATETIME()), 'Sold'),
(@Rahul, @Sig, N'Very Good', 550.00, N'Signals and Systems textbook.', DATEADD(day, -12, SYSDATETIME()), 'Sold'),
(@Sneha, @Net, N'Good', 500.00, N'Computer Networks 5th Edition.', DATEADD(day, -6, SYSDATETIME()), 'Sold'),
(@Abhinav, @Calc, N'Very Good', 700.00, N'Calculus book for first year.', DATEADD(day, -4, SYSDATETIME()), 'Reserved');
GO

-- 5. Populate Orders
DECLARE @BuyerAbhinav INT = (SELECT UserID FROM dbo.Users WHERE Username = N'abhinav_r');
DECLARE @BuyerPrasanth INT = (SELECT UserID FROM dbo.Users WHERE Username = N'prasanth_r');
DECLARE @BuyerPriya INT = (SELECT UserID FROM dbo.Users WHERE Username = N'priya_d');

-- Order 1: Buyer Priya purchases Prasanth's Intro to Algo listing
INSERT INTO dbo.Orders (BuyerID, OrderDate, TotalAmount, ShippingAddress, PaymentStatus, OrderStatus) VALUES
(@BuyerPriya, DATEADD(day, -14, SYSDATETIME()), 800.00, N'LHR Hostel, IIT Bhubaneswar', 'Paid', 'Delivered');

-- Order 2: Buyer Prasanth purchases Rahul's Signals and Systems listing
INSERT INTO dbo.Orders (BuyerID, OrderDate, TotalAmount, ShippingAddress, PaymentStatus, OrderStatus) VALUES
(@BuyerPrasanth, DATEADD(day, -11, SYSDATETIME()), 550.00, N'MHR Hostel, IIT Bhubaneswar', 'Paid', 'Delivered');

-- Order 3: Buyer Abhinav purchases Sneha's Computer Networks listing
INSERT INTO dbo.Orders (BuyerID, OrderDate, TotalAmount, ShippingAddress, PaymentStatus, OrderStatus) VALUES
(@BuyerAbhinav, DATEADD(day, -5, SYSDATETIME()), 500.00, N'MHR Hostel, IIT Bhubaneswar', 'Paid', 'Delivered');
GO

-- 6. Populate OrderItems
DECLARE @Order1 INT = (SELECT OrderID FROM dbo.Orders WHERE TotalAmount = 800.00 AND BuyerID = (SELECT UserID FROM dbo.Users WHERE Username = N'priya_d'));
DECLARE @Order2 INT = (SELECT OrderID FROM dbo.Orders WHERE TotalAmount = 550.00 AND BuyerID = (SELECT UserID FROM dbo.Users WHERE Username = N'prasanth_r'));
DECLARE @Order3 INT = (SELECT OrderID FROM dbo.Orders WHERE TotalAmount = 500.00 AND BuyerID = (SELECT UserID FROM dbo.Users WHERE Username = N'abhinav_r'));

DECLARE @ListSoldAlgo INT = (SELECT ListingID FROM dbo.Listings WHERE Price = 800.00 AND ListingStatus = 'Sold');
DECLARE @ListSoldSig INT = (SELECT ListingID FROM dbo.Listings WHERE Price = 550.00 AND ListingStatus = 'Sold');
DECLARE @ListSoldNet INT = (SELECT ListingID FROM dbo.Listings WHERE Price = 500.00 AND ListingStatus = 'Sold');

INSERT INTO dbo.OrderItems (OrderID, ListingID, PriceAtPurchase) VALUES
(@Order1, @ListSoldAlgo, 800.00),
(@Order2, @ListSoldSig, 550.00),
(@Order3, @ListSoldNet, 500.00);
GO

-- 7. Populate Reviews
DECLARE @Item1 INT = (SELECT OrderItemID FROM dbo.OrderItems WHERE PriceAtPurchase = 800.00);
DECLARE @Item2 INT = (SELECT OrderItemID FROM dbo.OrderItems WHERE PriceAtPurchase = 550.00);
DECLARE @Item3 INT = (SELECT OrderItemID FROM dbo.OrderItems WHERE PriceAtPurchase = 500.00);

DECLARE @PriyaID INT = (SELECT UserID FROM dbo.Users WHERE Username = N'priya_d');
DECLARE @PrasanthID INT = (SELECT UserID FROM dbo.Users WHERE Username = N'prasanth_r');
DECLARE @AbhinavID INT = (SELECT UserID FROM dbo.Users WHERE Username = N'abhinav_r');

INSERT INTO dbo.Reviews (OrderItemID, ReviewerID, Rating, Comment, ReviewDate) VALUES
(@Item1, @PriyaID, 5, N'Book is in perfect condition! Extremely fast handoff on campus.', DATEADD(day, -13, SYSDATETIME())),
(@Item2, @PrasanthID, 4, N'Good interaction. Book condition was exactly as described.', DATEADD(day, -10, SYSDATETIME())),
(@Item3, @AbhinavID, 5, N'Excellent seller. She brought it right to my hostel gate.', DATEADD(day, -4, SYSDATETIME()));
GO
