-- =========================================================================
-- Project: Gyan Pustak - Library & Marketplace Database
-- Script: Schema Definition for SQLite (Auto-initialized on startup)
-- =========================================================================

-- Drop tables in reverse order of dependency
DROP TABLE IF EXISTS TicketMessages;
DROP TABLE IF EXISTS SupportTickets;
DROP TABLE IF EXISTS OrderItems;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Listings;
DROP TABLE IF EXISTS Reservations;
DROP TABLE IF EXISTS BorrowedBooks;
DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Users;

-- 1. Users Table
CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL UNIQUE,
    Email TEXT NOT NULL UNIQUE,
    PasswordHash TEXT NOT NULL,
    Phone TEXT,
    CollegeName TEXT NOT NULL,
    DateJoined TEXT DEFAULT (datetime('now', 'localtime')),
    UserStatus TEXT DEFAULT 'Active', -- 'Active', 'Suspended'
    Role TEXT NOT NULL CHECK (Role IN ('Student', 'Admin', 'SuperAdmin'))
);

-- 2. Categories Table
CREATE TABLE Categories (
    CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    CategoryName TEXT NOT NULL UNIQUE,
    Description TEXT
);

-- 3. Books Table (General Catalog & Library Inventory)
CREATE TABLE Books (
    BookID INTEGER PRIMARY KEY AUTOINCREMENT,
    ISBN TEXT NOT NULL UNIQUE,
    Title TEXT NOT NULL,
    Author TEXT NOT NULL,
    Edition TEXT,
    Publisher TEXT,
    PublicationYear INTEGER,
    CategoryID INTEGER NOT NULL,
    TotalCopies INTEGER DEFAULT 1,
    AvailableCopies INTEGER DEFAULT 1,
    FOREIGN KEY (CategoryID) REFERENCES Categories (CategoryID) ON DELETE RESTRICT
);

-- 4. Listings Table (Bookstore products for sale)
CREATE TABLE Listings (
    ListingID INTEGER PRIMARY KEY AUTOINCREMENT,
    BookID INTEGER NOT NULL,
    SellerID INTEGER NOT NULL,
    Condition TEXT NOT NULL CHECK (Condition IN ('New', 'Like New', 'Very Good', 'Good', 'Acceptable')),
    Price REAL NOT NULL CHECK (Price > 0),
    ListingDescription TEXT,
    Stock INTEGER DEFAULT 1 CHECK (Stock >= 0),
    DateListed TEXT DEFAULT (datetime('now', 'localtime')),
    ListingStatus TEXT DEFAULT 'Active' CHECK (ListingStatus IN ('Active', 'Inactive')),
    FOREIGN KEY (BookID) REFERENCES Books (BookID) ON DELETE CASCADE,
    FOREIGN KEY (SellerID) REFERENCES Users (UserID) ON DELETE CASCADE
);

-- 5. BorrowedBooks Table
CREATE TABLE BorrowedBooks (
    BorrowID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    BookID INTEGER NOT NULL,
    BorrowDate TEXT,
    DueDate TEXT,
    ReturnDate TEXT,
    Status TEXT DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Approved', 'Rejected', 'Returned', 'Overdue')),
    FOREIGN KEY (UserID) REFERENCES Users (UserID) ON DELETE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Books (BookID) ON DELETE CASCADE
);

-- 6. Reservations Table (For unavailable books)
CREATE TABLE Reservations (
    ReservationID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    BookID INTEGER NOT NULL,
    ReservationDate TEXT DEFAULT (datetime('now', 'localtime')),
    Status TEXT DEFAULT 'Active' CHECK (Status IN ('Active', 'Fulfilled', 'Cancelled')),
    FOREIGN KEY (UserID) REFERENCES Users (UserID) ON DELETE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Books (BookID) ON DELETE CASCADE
);

-- 7. Orders Table
CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    BuyerID INTEGER NOT NULL,
    OrderDate TEXT DEFAULT (datetime('now', 'localtime')),
    TotalAmount REAL NOT NULL CHECK (TotalAmount >= 0),
    ShippingAddress TEXT NOT NULL,
    PaymentStatus TEXT DEFAULT 'Pending' CHECK (PaymentStatus IN ('Pending', 'Paid', 'Failed')),
    OrderStatus TEXT DEFAULT 'Pending' CHECK (OrderStatus IN ('Pending', 'Approved', 'Cancelled', 'Shipped', 'Delivered')),
    FOREIGN KEY (BuyerID) REFERENCES Users (UserID) ON DELETE CASCADE
);

-- 8. OrderItems Table
CREATE TABLE OrderItems (
    OrderItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID INTEGER NOT NULL,
    ListingID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL CHECK (Quantity > 0),
    PriceAtPurchase REAL NOT NULL CHECK (PriceAtPurchase > 0),
    FOREIGN KEY (OrderID) REFERENCES Orders (OrderID) ON DELETE CASCADE,
    FOREIGN KEY (ListingID) REFERENCES Listings (ListingID) ON DELETE RESTRICT
);

-- 9. SupportTickets Table
CREATE TABLE SupportTickets (
    TicketID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    Subject TEXT NOT NULL,
    Category TEXT NOT NULL CHECK (Category IN ('Library', 'Store', 'Account', 'Technical', 'Other')),
    Description TEXT NOT NULL,
    Status TEXT DEFAULT 'Open' CHECK (Status IN ('Open', 'In Progress', 'Resolved')),
    DateCreated TEXT DEFAULT (datetime('now', 'localtime')),
    DateUpdated TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (UserID) REFERENCES Users (UserID) ON DELETE CASCADE
);

-- 10. TicketMessages Table (For support chat)
CREATE TABLE TicketMessages (
    MessageID INTEGER PRIMARY KEY AUTOINCREMENT,
    TicketID INTEGER NOT NULL,
    SenderID INTEGER NOT NULL,
    MessageText TEXT NOT NULL,
    DateSent TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (TicketID) REFERENCES SupportTickets (TicketID) ON DELETE CASCADE,
    FOREIGN KEY (SenderID) REFERENCES Users (UserID) ON DELETE CASCADE
);
