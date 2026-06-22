-- 7. Dim_Feats (Intermediate table per la bridge table)
IF OBJECT_ID('dbo.Dim_Feats') IS NOT NULL DROP TABLE dbo.Dim_Feats;
CREATE TABLE dbo.Dim_Feats (
    Feats_Code_PK INT IDENTITY(1,1) NOT NULL PRIMARY KEY
);
GO