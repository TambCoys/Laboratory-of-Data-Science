-- 3. Dim_Artist_SSIS
IF OBJECT_ID('dbo.Dim_Artist_SSIS') IS NOT NULL 
    DROP TABLE dbo.Dim_Artist_SSIS;
GO

CREATE TABLE dbo.Dim_Artist_SSIS (
    Artist_Code_PK     INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    Artist_Geo_Code_FK INT  NOT NULL,   
    Name               NVARCHAR(200) NULL,
    Gender             CHAR(1)       NULL,
    Nationality        NVARCHAR(50)  NULL,

    CONSTRAINT FK_Artist_Geo_SSIS
        FOREIGN KEY (Artist_Geo_Code_FK)
        REFERENCES dbo.Dim_Artist_Geography_SSIS(Artist_Geo_Code_PK)
);
GO
