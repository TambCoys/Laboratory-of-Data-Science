--DimArtistGeo

USE [Group_ID_4_DB];
GO

-- 1. Dim_Artist_Geography_SSIS
IF OBJECT_ID('dbo.Dim_Artist_Geography_SSIS') IS NOT NULL 
    DROP TABLE dbo.Dim_Artist_Geography_SSIS;
GO

CREATE TABLE dbo.Dim_Artist_Geography_SSIS (
    Artist_Geo_Code_PK INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    H3_Code            VARCHAR(50) NULL,
    Country            NVARCHAR(100) NULL,
    Region             NVARCHAR(100) NULL,
    Province           NVARCHAR(100) NULL,
    City               NVARCHAR(100) NULL
);
GO
