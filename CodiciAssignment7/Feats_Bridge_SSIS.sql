-- 8. BridgeTable SSIS

IF OBJECT_ID('dbo.Feats_Bridge_SSIS', 'U') IS NOT NULL 
    DROP TABLE dbo.Feats_Bridge_SSIS;
GO

CREATE TABLE dbo.Feats_Bridge_SSIS (
    Feat_Artist_Code_FK INT NOT NULL,
    Feats_Code_FK INT NOT NULL,  

    CONSTRAINT PK_Bridge_SSIS PRIMARY KEY (Feat_Artist_Code_FK, Feats_Code_FK)
);
GO

-- VINCOLI DI FOREIGN KEY --

ALTER TABLE dbo.Feats_Bridge_SSIS
ADD CONSTRAINT FK_Bridge_Artist_SSIS
    FOREIGN KEY (Feat_Artist_Code_FK)
    REFERENCES dbo.Dim_Artist_SSIS(Artist_Code_PK);
GO

ALTER TABLE dbo.Feats_Bridge_SSIS
ADD CONSTRAINT FK_Bridge_Feats_SSIS
    FOREIGN KEY (Feats_Code_FK)
    REFERENCES dbo.Dim_Feats_SSIS(Feats_Code_PK);
GO
