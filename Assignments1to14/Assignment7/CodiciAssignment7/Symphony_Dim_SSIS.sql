-- 5. Dim_Symphony_SSIS
IF OBJECT_ID('dbo.Dim_Symphony_SSIS') IS NOT NULL 
    DROP TABLE dbo.Dim_Symphony_SSIS;
GO

CREATE TABLE dbo.Dim_Symphony_SSIS (
    Symphony_Code_PK     INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
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
