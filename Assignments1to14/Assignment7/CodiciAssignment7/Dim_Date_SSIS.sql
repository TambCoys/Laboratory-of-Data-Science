-- 4. Dim_Date_SSIS
IF OBJECT_ID('dbo.Dim_Date_SSIS') IS NOT NULL 
    DROP TABLE dbo.Dim_Date_SSIS;
GO

CREATE TABLE dbo.Dim_Date_SSIS (
    Date_Code_PK INT IDENTITY(1,1) NOT NULL PRIMARY KEY,   -- diverso dal giorno
    Year         INT       NOT NULL,
    Month        INT       NOT NULL,
    Day          INT       NOT NULL,
    Season       VARCHAR(10) NULL
);
GO
