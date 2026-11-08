-- =========================================================================
-- Project: GyanPustak - College Textbook Marketplace Database
-- Script: Advanced Marketplace & Analytics Queries
-- Target RDBMS: Microsoft SQL Server (T-SQL)
-- Description: Demonstrates SQL competency including multi-table JOINs, 
--              aggregates, subqueries, and analytical window functions.
-- =========================================================================

-- USE GyanPustak;
-- GO

-- =========================================================================
-- Query 1: Core Marketplace Book Search
-- Rationale: Displays list of active book listings for buyers. 
-- Features: INNER JOINs (4 tables), filters by Category and Seller College, 
--           and orders by price ascending.
-- =========================================================================
SELECT 
    l.ListingID,
    b.Title AS BookTitle,
    b.Author,
    c.CategoryName,
    l.Condition,
    l.Price,
    s.Username AS SellerName,
    s.CollegeName AS College
FROM 
    dbo.Listings l
    INNER JOIN dbo.Books b ON l.BookID = b.BookID
    INNER JOIN dbo.Categories c ON b.CategoryID = c.CategoryID
    INNER JOIN dbo.Users s ON l.SellerID = s.UserID
WHERE 
    l.ListingStatus = 'Active'
    AND s.UserStatus = 'Active'
    AND c.CategoryName = N'Computer Science'
    AND s.CollegeName = N'IIT Bhubaneswar'
ORDER BY 
    l.Price ASC;
GO

-- =========================================================================
-- Query 2: College Campus Sales Report
-- Rationale: Business reporting query showing sales volume and revenue by college.
-- Features: JOINs, GROUP BY, Aggregate functions (COUNT, SUM, AVG, MAX).
-- =========================================================================
SELECT 
    u.CollegeName,
    COUNT(DISTINCT o.OrderID) AS CompletedOrders,
    COUNT(oi.OrderItemID) AS TotalBooksSold,
    SUM(oi.PriceAtPurchase) AS TotalRevenue,
    AVG(oi.PriceAtPurchase) AS AverageBookPrice,
    MAX(oi.PriceAtPurchase) AS MostExpensiveBookSold
FROM 
    dbo.Users u
    INNER JOIN dbo.Orders o ON u.UserID = o.BuyerID
    INNER JOIN dbo.OrderItems oi ON o.OrderID = oi.OrderID
WHERE 
    o.PaymentStatus = 'Paid'
GROUP BY 
    u.CollegeName
ORDER BY 
    TotalRevenue DESC;
GO

-- =========================================================================
-- Query 3: Bargain Finder (Underpriced Listings)
-- Rationale: Identifies textbook listings priced lower than the average 
--            market value of that book across all listings. Helps buyers find deals!
-- Features: Correlated Subquery with aggregates.
-- =========================================================================
SELECT 
    b.Title,
    b.Author,
    l.Condition,
    l.Price AS ListingPrice,
    MarketAvg.AvgPrice AS AverageMarketPrice,
    (MarketAvg.AvgPrice - l.Price) AS SavingsAmount
FROM 
    dbo.Listings l
    INNER JOIN dbo.Books b ON l.BookID = b.BookID
    -- Inline subquery calculating average price per book (ISBN)
    INNER JOIN (
        SELECT BookID, AVG(Price) AS AvgPrice
        FROM dbo.Listings
        GROUP BY BookID
    ) MarketAvg ON l.BookID = MarketAvg.BookID
WHERE 
    l.ListingStatus = 'Active'
    AND l.Price < MarketAvg.AvgPrice
ORDER BY 
    SavingsAmount DESC;
GO

-- =========================================================================
-- Query 4: Top Sellers Ranking
-- Rationale: Ranks marketplace sellers by revenue using SQL Server Analytical Functions.
-- Features: Window Functions (DENSE_RANK), joins, aggregates.
-- =========================================================================
SELECT 
    u.UserID AS SellerID,
    u.Username AS SellerName,
    u.CollegeName AS College,
    SUM(oi.PriceAtPurchase) AS TotalRevenue,
    COUNT(oi.OrderItemID) AS CopiesSold,
    DENSE_RANK() OVER (ORDER BY SUM(oi.PriceAtPurchase) DESC) AS RevenueRank
FROM 
    dbo.Users u
    INNER JOIN dbo.Listings l ON u.UserID = l.SellerID
    INNER JOIN dbo.OrderItems oi ON l.ListingID = oi.ListingID
    INNER JOIN dbo.Orders o ON oi.OrderID = o.OrderID
WHERE 
    o.PaymentStatus = 'Paid'
GROUP BY 
    u.UserID, u.Username, u.CollegeName;
GO

-- =========================================================================
-- Query 5: Seller Feedback Breakdown
-- Rationale: Trace transaction reviews for listings to build trust profiles.
-- Features: LEFT JOINs, conditional rating checks.
-- =========================================================================
SELECT 
    u.Username AS SellerName,
    COUNT(r.ReviewID) AS TotalReviews,
    AVG(CAST(r.Rating AS FLOAT)) AS SellerRating,
    SUM(CASE WHEN r.Rating = 5 THEN 1 ELSE 0 END) AS FiveStarCount,
    SUM(CASE WHEN r.Rating <= 2 THEN 1 ELSE 0 END) AS LowRatingCount
FROM 
    dbo.Users u
    INNER JOIN dbo.Listings l ON u.UserID = l.SellerID
    INNER JOIN dbo.OrderItems oi ON l.ListingID = oi.ListingID
    LEFT JOIN dbo.Reviews r ON oi.OrderItemID = r.OrderItemID
GROUP BY 
    u.Username
ORDER BY 
    SellerRating DESC;
GO
