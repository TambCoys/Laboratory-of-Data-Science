-- 6. Dim_Symphony_Category (melodia – da Assignment 3)
IF OBJECT_ID('dbo.Dim_Symphony') IS NOT NULL DROP TABLE dbo.Dim_Symphony;
CREATE TABLE dbo.Dim_Symphony (
    Symphony_Code_PK     VARCHAR(10) IDENTITY(1,1) PRIMARY KEY,
    BPM                  FLOAT NULL,
    Rolloff              FLOAT NULL,
    Flux                 FLOAT NULL,
    RMS                  FLOAT NULL,
    Flatness             FLOAT NULL,
    Spectral_Complexity  FLOAT NULL,
    Pitch                FLOAT NULL,
    Loudness             FLOAT NULL
);
GO