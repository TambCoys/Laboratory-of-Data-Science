-- 4. Dim_Date
IF OBJECT_ID('dbo.Dim_Date') IS NOT NULL DROP TABLE dbo.Dim_Date;
CREATE TABLE dbo.Dim_Date (
    Date_Code_PK INT PRIMARY KEY,      -- diverso dal giorno
    Year        INT       NOT NULL,
    Month       INT       NOT NULL,
    Day         INT       NOT NULL,
    Season      VARCHAR(10) NULL
);
GO
