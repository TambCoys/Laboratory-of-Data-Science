-- 7. Dim_Feats_SSIS (Intermediate table per la bridge table)
IF OBJECT_ID('dbo.Dim_Feats_SSIS') IS NOT NULL 
    DROP TABLE dbo.Dim_Feats_SSIS;
GO

CREATE TABLE dbo.Dim_Feats_SSIS (
    Feats_Code_PK INT IDENTITY(1,1) NOT NULL PRIMARY KEY
);
GO
