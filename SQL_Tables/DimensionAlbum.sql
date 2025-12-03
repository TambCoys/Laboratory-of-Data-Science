IF OBJECT_ID('dbo.Dim_Album') IS NOT NULL DROP TABLE dbo.Dim_Album;
CREATE TABLE dbo.Dim_Album (
    Album_Code_PK INT IDENTITY(1,1) PRIMARY KEY,
    AlbumTitle VARCHAR(200) NULL,
    AlbumType  VARCHAR(50) NULL,        -- album, single, ep...
);
