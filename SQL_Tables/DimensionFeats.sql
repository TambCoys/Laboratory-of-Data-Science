-- 7. Dim_Feats (Intermediate table per la bridge table)
IF OBJECT_ID('dbo.Dim_Feats', 'U') IS NOT NULL 
    DROP TABLE dbo.Dim_Feats;
GO

CREATE TABLE dbo.Dim_Feats (
    Feats_Code_PK VARCHAR(10) NOT NULL PRIMARY KEY
);
GO
