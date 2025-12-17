--Dim_Album_SSIS

IF OBJECT_ID('dbo.Dim_Album_SSIS', 'U') IS NOT NULL
    DROP TABLE dbo.Dim_Album_SSIS;

CREATE TABLE dbo.Dim_Album_SSIS (
    Album_Code_PK INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    AlbumTitle VARCHAR(200) NULL,
    AlbumType VARCHAR(50) NULL
);

