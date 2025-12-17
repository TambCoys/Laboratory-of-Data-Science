--9. PublishedSong_Fact_SSIS

USE [Group_ID_4_DB];
GO

IF OBJECT_ID('dbo.PublishedSong_Fact_SSIS', 'U') IS NOT NULL 
    DROP TABLE dbo.PublishedSong_Fact_SSIS;
GO

CREATE TABLE dbo.PublishedSong_Fact_SSIS (
    Artist_Code_FK      INT NOT NULL,   
    Album_Code_FK       INT NOT NULL,   
    Date_Code_FK        INT NOT NULL,   
    Symphony_Code_FK    INT NOT NULL,   
    Text_Code_FK        INT NOT NULL,
    Feats_Code_FK       INT NOT NULL,

    Track_ID            VARCHAR(100) NOT NULL,

    Title               NVARCHAR(255) NOT NULL, 
    Duration_Sec        BIGINT        NULL,
    Streams_First_Month BIGINT        NULL,
    Popularity          INT           NULL,
    Category            VARCHAR(20)   NOT NULL,

    CONSTRAINT PK_Fact_SSIS PRIMARY KEY (
        Artist_Code_FK, 
        Album_Code_FK, 
        Date_Code_FK, 
        Symphony_Code_FK, 
        Text_Code_FK, 
        Feats_Code_FK
    )
);
GO

-- VINCOLI DI FOREIGN KEY --

ALTER TABLE dbo.PublishedSong_Fact_SSIS
ADD CONSTRAINT FK_Fact_Artist_SSIS
    FOREIGN KEY (Artist_Code_FK)
    REFERENCES dbo.Dim_Artist_SSIS(Artist_Code_PK);
GO

ALTER TABLE dbo.PublishedSong_Fact_SSIS
ADD CONSTRAINT FK_Fact_Album_SSIS
    FOREIGN KEY (Album_Code_FK)
    REFERENCES dbo.Dim_Album_SSIS(Album_Code_PK);
GO

ALTER TABLE dbo.PublishedSong_Fact_SSIS
ADD CONSTRAINT FK_Fact_Date_SSIS
    FOREIGN KEY (Date_Code_FK)
    REFERENCES dbo.Dim_Date_SSIS(Date_Code_PK);
GO

ALTER TABLE dbo.PublishedSong_Fact_SSIS
ADD CONSTRAINT FK_Fact_Symphony_SSIS
    FOREIGN KEY (Symphony_Code_FK)
    REFERENCES dbo.Dim_Symphony_SSIS(Symphony_Code_PK);
GO

ALTER TABLE dbo.PublishedSong_Fact_SSIS
ADD CONSTRAINT FK_Fact_Text_SSIS
    FOREIGN KEY (Text_Code_FK)
    REFERENCES dbo.Dim_Text_SSIS(Text_Code_PK);
GO

ALTER TABLE dbo.PublishedSong_Fact_SSIS
ADD CONSTRAINT FK_Fact_Feats_SSIS
    FOREIGN KEY (Feats_Code_FK)
    REFERENCES dbo.Dim_Feats_SSIS(Feats_Code_PK);
GO
