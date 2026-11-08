-- =========================================================================
-- Project: GyanPustak - College Textbook Marketplace Database
-- Script: Views Creation
-- Target RDBMS: Microsoft SQL Server (T-SQL)
-- Description: Creates SQL views to abstract complex JOINs, simplifying 
--              retrieval for front-end APIs and analytics reporting.
-- =========================================================================

-- USE GyanPustak;
-- GO

-- Drop existing views if they exist
IF OBJECT_ID('dbo.vw_ActiveListings', 'V') IS NOT NULL DROP VIEW dbo.vw_ActiveListings;
IF OBJECT_ID('dbo.vw_CollegeSalesSummary', 'V') IS NOT NULL DROP VIEW dbo.vw_CollegeSalesSummary;
IF OBJECT_ID('dbo.vw_SellerPerformance', 'V') IS NOT NULL DROP VIEW dbo.vw_SellerPerformance;
GO

-- =========================================================================
-- 1. Active Listings View
-- Description: Consolidates active listings with book meta-data, category, 
--              and seller contact information for buyers.
-- =========================================================================
CREATE VIEW dbo.vw_ActiveListings AS
SELECT 
    l.ListingID,
    b.ISBN,
    b.Title AS BookTitle,
    b.Author,
    b.Edition,
    c.CategoryName,
    l.Condition,
    l.Price,
    l.ListingDescription,
    l.DateListed,
    s.UserID AS SellerID,
    s.Username AS SellerUsername,
    s.Email AS SellerEmail,
    s.CollegeName AS SellerCollege
FROM 
    dbo.Listings l
    INNER JOIN dbo.Books b ON l.BookID = b.BookID
    INNER JOIN dbo.Categories c ON b.CategoryID = c.CategoryID
    INNER JOIN dbo.Users s ON l.SellerID = s.UserID
WHERE 
    l.ListingStatus = 'Active'
    AND s.UserStatus = 'Active';
GO

-- =========================================================================
-- 2. College Sales Summary View
-- Description: Aggregates sales volume, total revenue, and average transaction
--              value based on the buyer's college campus.
-- =========================================================================
CREATE VIEW dbo.vw_CollegeSalesSummary AS
SELECT 
    u.CollegeName AS BuyerCollege,
    COUNT(DISTINCT o.OrderID) AS TotalOrders,
    COUNT(oi.OrderItemID) AS TotalBooksSold,
    SUM(oi.PriceAtPurchase) AS TotalRevenue,
    ROUND(AVG(oi.PriceAtPurchase), 2) AS AverageBookPrice
FROM 
    dbo.Users u
    INNER JOIN dbo.Orders o ON u.UserID = o.BuyerID
    INNER JOIN dbo.OrderItems oi ON o.OrderID = oi.OrderID
WHERE 
    o.PaymentStatus = 'Paid'
GROUP BY 
    u.CollegeName;
GO

-- =========================================================================
-- 3. Seller Performance View
-- Description: Summarizes each seller's inventory count, quantity sold, 
--              total revenue earned, and average feedback rating received.
-- =========================================================================
CREATE VIEW dbo.vw_SellerPerformance AS
SELECT 
    u.UserID AS SellerID,
    u.Username,
    u.CollegeName,
    COUNT(DISTINCT l.ListingID) AS TotalListingsCreated,
    SUM(CASE WHEN l.ListingStatus = 'Sold' THEN 1 ELSE 0 END) AS BooksSold,
    ISNULL(SUM(oi.PriceAtPurchase), 0.00) AS TotalRevenue,
    ROUND(AVG(CAST(r.Rating AS DECIMAL(3,2))), 2) AS AverageRating
FROM 
    dbo.Users u
    LEFT JOIN dbo.Listings l ON u.UserID = l.SellerID
    LEFT JOIN dbo.OrderItems oi ON l.ListingID = oi.ListingID
    LEFT JOIN dbo.Reviews r ON oi.OrderItemID = r.OrderItemID
GROUP BY 
    u.UserID, u.Username, u.CollegeName;
GO
