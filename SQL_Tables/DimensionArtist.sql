-- 1. Dim_Artist 
IF OBJECT_ID('dbo.Dim_Artist') IS NOT NULL DROP TABLE dbo.Dim_Artist;
CREATE TABLE dbo.Dim_Artist (
    Artist_Code_PK     INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    Artist_Geo_Code_FK INT  NOT NULL,   
    Name               NVARCHAR(200) NULL,
    Gender             CHAR(1)       NULL,
    Nationality        NVARCHAR(50)  NULL,

 CONSTRAINT FK_Artist_Geo
        FOREIGN KEY (Artist_Geo_Code_FK)
        REFERENCES dbo.Dim_Artist_Geography(Artist_Geo_Code_PK)
        );
GO