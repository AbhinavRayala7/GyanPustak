-- =========================================================================
-- Project: GyanPustak - College Textbook Marketplace Database
-- Script: Schema Definition (DDL)
-- Target RDBMS: Microsoft SQL Server (T-SQL)
-- Description: Creates the relational schema for the peer-to-peer textbook 
--              marketplace, enforcing PK, FK, and integrity check constraints.
-- =========================================================================

-- Create Database if not exists (Note: Run this in master or your preferred context)
-- CREATE DATABASE GyanPustak;
-- GO
-- USE GyanPustak;
-- GO

-- Drop existing tables to ensure clean execution (in reverse order of dependencies)
IF OBJECT_ID('dbo.Reviews', 'U') IS NOT NULL DROP TABLE dbo.Reviews;
IF OBJECT_ID('dbo.OrderItems', 'U') IS NOT NULL DROP TABLE dbo.OrderItems;
IF OBJECT_ID('dbo.Orders', 'U') IS NOT NULL DROP TABLE dbo.Orders;
IF OBJECT_ID('dbo.Listings', 'U') IS NOT NULL DROP TABLE dbo.Listings;
IF OBJECT_ID('dbo.Books', 'U') IS NOT NULL DROP TABLE dbo.Books;
IF OBJECT_ID('dbo.Categories', 'U') IS NOT NULL DROP TABLE dbo.Categories;
IF OBJECT_ID('dbo.Users', 'U') IS NOT NULL DROP TABLE dbo.Users;
GO

-- ==========================================
-- 1. Users Table
-- ==========================================
CREATE TABLE dbo.Users (
    UserID INT IDENTITY(1,1) CONSTRAINT PK_Users PRIMARY KEY,
    Username NVARCHAR(50) NOT NULL CONSTRAINT UQ_Users_Username UNIQUE,
    Email NVARCHAR(100) NOT NULL CONSTRAINT UQ_Users_Email UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL, -- Storing hashed password representation
    Phone VARCHAR(15) NULL,
    CollegeName NVARCHAR(100) NOT NULL,
    DateJoined DATETIME2 CONSTRAINT DF_Users_DateJoined DEFAULT SYSDATETIME(),
    UserStatus VARCHAR(15) NOT NULL CONSTRAINT DF_Users_Status DEFAULT 'Active',
    
    -- Integrity Constraints
    CONSTRAINT CK_Users_Status CHECK (UserStatus IN ('Active', 'Suspended', 'Inactive')),
    CONSTRAINT CK_Users_Email CHECK (Email LIKE '%_@__%.__%') -- Simple basic email format check
);
GO

-- ==========================================
-- 2. Categories Table
-- ==========================================
CREATE TABLE dbo.Categories (
    CategoryID INT IDENTITY(1,1) CONSTRAINT PK_Categories PRIMARY KEY,
    CategoryName NVARCHAR(50) NOT NULL CONSTRAINT UQ_Categories_Name UNIQUE,
    Description NVARCHAR(255) NULL
);
GO

-- ==========================================
-- 3. Books Table
-- ==========================================
CREATE TABLE dbo.Books (
    BookID INT IDENTITY(1,1) CONSTRAINT PK_Books PRIMARY KEY,
    ISBN VARCHAR(13) NOT NULL CONSTRAINT UQ_Books_ISBN UNIQUE,
    Title NVARCHAR(150) NOT NULL,
    Author NVARCHAR(100) NOT NULL,
    Edition VARCHAR(10) NULL,
    Publisher NVARCHAR(100) NULL,
    PublicationYear INT NULL,
    CategoryID INT NOT NULL,
    
    -- Integrity Constraints
    CONSTRAINT FK_Books_Categories FOREIGN KEY (CategoryID) REFERENCES dbo.Categories(CategoryID) ON DELETE NO ACTION,
    CONSTRAINT CK_Books_ISBN CHECK (LEN(ISBN) = 13 AND ISBN LIKE '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    CONSTRAINT CK_Books_Year CHECK (PublicationYear >= 1900 AND PublicationYear <= YEAR(SYSDATETIME()) + 1)
);
GO

-- ==========================================
-- 4. Listings Table
-- ==========================================
CREATE TABLE dbo.Listings (
    ListingID INT IDENTITY(1,1) CONSTRAINT PK_Listings PRIMARY KEY,
    SellerID INT NOT NULL,
    BookID INT NOT NULL,
    Condition NVARCHAR(20) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    ListingDescription NVARCHAR(500) NULL,
    DateListed DATETIME2 CONSTRAINT DF_Listings_DateListed DEFAULT SYSDATETIME(),
    ListingStatus VARCHAR(15) NOT NULL CONSTRAINT DF_Listings_Status DEFAULT 'Active',
    
    -- Integrity Constraints
    CONSTRAINT FK_Listings_Users FOREIGN KEY (SellerID) REFERENCES dbo.Users(UserID) ON DELETE CASCADE,
    CONSTRAINT FK_Listings_Books FOREIGN KEY (BookID) REFERENCES dbo.Books(BookID) ON DELETE CASCADE,
    CONSTRAINT CK_Listings_Condition CHECK (Condition IN (N'New', N'Like New', N'Very Good', N'Good', N'Acceptable')),
    CONSTRAINT CK_Listings_Price CHECK (Price > 0.00),
    CONSTRAINT CK_Listings_Status CHECK (ListingStatus IN ('Active', 'Sold', 'Inactive', 'Reserved'))
);
GO

-- ==========================================
-- 5. Orders Table
-- ==========================================
CREATE TABLE dbo.Orders (
    OrderID INT IDENTITY(1,1) CONSTRAINT PK_Orders PRIMARY KEY,
    BuyerID INT NOT NULL,
    OrderDate DATETIME2 CONSTRAINT DF_Orders_OrderDate DEFAULT SYSDATETIME(),
    TotalAmount DECIMAL(10,2) NOT NULL,
    ShippingAddress NVARCHAR(255) NOT NULL,
    PaymentStatus VARCHAR(15) NOT NULL CONSTRAINT DF_Orders_PaymentStatus DEFAULT 'Pending',
    OrderStatus VARCHAR(15) NOT NULL CONSTRAINT DF_Orders_OrderStatus DEFAULT 'Processing',
    
    -- Integrity Constraints
    CONSTRAINT FK_Orders_Users FOREIGN KEY (BuyerID) REFERENCES dbo.Users(UserID) ON DELETE NO ACTION,
    CONSTRAINT CK_Orders_Total CHECK (TotalAmount >= 0.00),
    CONSTRAINT CK_Orders_PaymentStatus CHECK (PaymentStatus IN ('Pending', 'Paid', 'Failed', 'Refunded')),
    CONSTRAINT CK_Orders_OrderStatus CHECK (OrderStatus IN ('Processing', 'Shipped', 'Delivered', 'Cancelled'))
);
GO

-- ==========================================
-- 6. OrderItems Table
-- ==========================================
CREATE TABLE dbo.OrderItems (
    OrderItemID INT IDENTITY(1,1) CONSTRAINT PK_OrderItems PRIMARY KEY,
    OrderID INT NOT NULL,
    ListingID INT NOT NULL,
    PriceAtPurchase DECIMAL(10,2) NOT NULL,
    
    -- Integrity Constraints
    CONSTRAINT FK_OrderItems_Orders FOREIGN KEY (OrderID) REFERENCES dbo.Orders(OrderID) ON DELETE CASCADE,
    CONSTRAINT FK_OrderItems_Listings FOREIGN KEY (ListingID) REFERENCES dbo.Listings(ListingID) ON DELETE NO ACTION,
    CONSTRAINT CK_OrderItems_Price CHECK (PriceAtPurchase > 0.00)
);
GO

-- ==========================================
-- 7. Reviews Table
-- ==========================================
CREATE TABLE dbo.Reviews (
    ReviewID INT IDENTITY(1,1) CONSTRAINT PK_Reviews PRIMARY KEY,
    OrderItemID INT NOT NULL CONSTRAINT UQ_Reviews_OrderItem UNIQUE, -- One review per ordered item
    ReviewerID INT NOT NULL,
    Rating INT NOT NULL,
    Comment NVARCHAR(500) NULL,
    ReviewDate DATETIME2 CONSTRAINT DF_Reviews_ReviewDate DEFAULT SYSDATETIME(),
    
    -- Integrity Constraints
    CONSTRAINT FK_Reviews_OrderItems FOREIGN KEY (OrderItemID) REFERENCES dbo.OrderItems(OrderItemID) ON DELETE CASCADE,
    CONSTRAINT FK_Reviews_Users FOREIGN KEY (ReviewerID) REFERENCES dbo.Users(UserID) ON DELETE NO ACTION,
    CONSTRAINT CK_Reviews_Rating CHECK (Rating >= 1 AND Rating <= 5)
);
GO
