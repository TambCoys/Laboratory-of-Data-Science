USE [Group_ID_4_DB];
GO

-- 1. Dim_Artist_Geography 
IF OBJECT_ID('dbo.Dim_Artist_Geography') IS NOT NULL DROP TABLE dbo.Dim_Artist_Geography;
CREATE TABLE dbo.Dim_Artist_Geography (
    Artist_Geo_Code_PK INT IDENTITY(1,1) PRIMARY KEY,
    H3_Code            VARCHAR(50) NULL,
    Country            NVARCHAR(100) NULL,
    Region             NVARCHAR(100) NULL,
    Province           NVARCHAR(100) NULL,
    City               NVARCHAR(100) NULL
);
GO