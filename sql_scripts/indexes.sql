-- =========================================================================
-- Project: GyanPustak - College Textbook Marketplace Database
-- Script: Index Definition & Performance Optimization
-- Target RDBMS: Microsoft SQL Server (T-SQL)
-- Description: Creates non-clustered, composite, and covering indexes to 
--              speed up JOINs, search filters, and aggregate reporting.
-- =========================================================================

-- USE GyanPustak;
-- GO

-- Drop existing indexes if they exist
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Books_CategoryID' AND object_id = OBJECT_ID('dbo.Books'))
    DROP INDEX IX_Books_CategoryID ON dbo.Books;
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Listings_SellerID' AND object_id = OBJECT_ID('dbo.Listings'))
    DROP INDEX IX_Listings_SellerID ON dbo.Listings;
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Listings_BookID' AND object_id = OBJECT_ID('dbo.Listings'))
    DROP INDEX IX_Listings_BookID ON dbo.Listings;
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Listings_Status_Price' AND object_id = OBJECT_ID('dbo.Listings'))
    DROP INDEX IX_Listings_Status_Price ON dbo.Listings;
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Users_College' AND object_id = OBJECT_ID('dbo.Users'))
    DROP INDEX IX_Users_College ON dbo.Users;
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_OrderItems_OrderID_ListingID' AND object_id = OBJECT_ID('dbo.OrderItems'))
    DROP INDEX IX_OrderItems_OrderID_ListingID ON dbo.OrderItems;
GO

-- =========================================================================
-- 1. Indexing Foreign Keys
-- Description: SQL Server automatically indexes Primary Keys (Clustered Index), 
--              but NOT Foreign Keys. Foreign key indexes dramatically improve 
--              multi-table JOIN operations.
-- =========================================================================

-- Index on Books(CategoryID) for joining Books and Categories
CREATE NONCLUSTERED INDEX IX_Books_CategoryID
ON dbo.Books (CategoryID);
GO

-- Index on Listings(SellerID) to quickly fetch listings created by a seller
CREATE NONCLUSTERED INDEX IX_Listings_SellerID
ON dbo.Listings (SellerID);
GO

-- Index on Listings(BookID) for joining Listings and Books
CREATE NONCLUSTERED INDEX IX_Listings_BookID
ON dbo.Listings (BookID);
GO

-- Composite Index on OrderItems(OrderID, ListingID) for order lookups
CREATE NONCLUSTERED INDEX IX_OrderItems_OrderID_ListingID
ON dbo.OrderItems (OrderID, ListingID);
GO

-- =========================================================================
-- 2. Covering & Composite Indexes for High-Frequency Searches
-- =========================================================================

-- Index on Users(CollegeName)
-- Optimization rationale: Buyers search for books listed at their own college 
-- campus. This index converts a full table scan on Users into a fast Index Seek 
-- when joining listings to filter by seller college.
CREATE NONCLUSTERED INDEX IX_Users_College
ON dbo.Users (CollegeName)
INCLUDE (Username, UserStatus); -- Covering index to prevent key lookups
GO

-- Composite Index on Listings(ListingStatus, Price)
-- Optimization rationale: Marketplace lists are filtered by 'Active' status 
-- and sorted/filtered by Price. Keeping status as the leading column allows 
-- SQL Server to instantly filter out sold/inactive items and seek the price range.
CREATE NONCLUSTERED INDEX IX_Listings_Status_Price
ON dbo.Listings (ListingStatus, Price)
INCLUDE (BookID, SellerID, Condition); -- Covering index for active lists
GO

/*
-- =========================================================================
-- Performance Verification Guidelines:
-- =========================================================================
To verify the performance improvement, run the following search query in 
SQL Server Management Studio (SSMS) with "Include Actual Execution Plan" (Ctrl+M) active:

SELECT b.Title, l.Price, u.Username, u.CollegeName
FROM dbo.Listings l
INNER JOIN dbo.Books b ON l.BookID = b.BookID
INNER JOIN dbo.Users u ON l.SellerID = u.UserID
WHERE u.CollegeName = N'IIT Bhubaneswar' AND l.ListingStatus = 'Active';

Before Indexing:
- The SQL Server Query Optimizer performs a Clustered Index Scan (equivalent to a table scan) 
  on Users to find matching colleges, and a scan on Listings.

After Indexing:
- The Query Optimizer uses an Index Seek on IX_Users_College (cost reduction > 70%) and 
  an Index Seek on IX_Listings_Status_Price, leading to minimal logical reads.
*/
