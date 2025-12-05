-- 8. BridgeTable

IF OBJECT_ID('dbo.Feats_Bridge', 'U') IS NOT NULL 
    DROP TABLE dbo.Feats_Bridge;
GO

CREATE TABLE dbo.Feats_Bridge (
    Feat_Artist_Code_FK    INT NOT NULL,
    Feats_Code_FK    INT NOT NULL,  

    CONSTRAINT PK_Bridge PRIMARY KEY (Feat_Artist_Code_FK, Feats_Code_FK)
);
GO

-- VINCOLI DI FOREIGN KEY--

ALTER TABLE dbo.Feats_Bridge
ADD CONSTRAINT FK_Bridge_Artist
    FOREIGN KEY (Feat_Artist_Code_FK)
    REFERENCES dbo.Dim_Artist(Artist_Code_PK);
GO

ALTER TABLE dbo.Feats_Bridge
ADD CONSTRAINT FK_Bridge_Feats
    FOREIGN KEY (Feats_Code_FK)
    REFERENCES dbo.Dim_Feats(Feats_Code_PK);

GO
