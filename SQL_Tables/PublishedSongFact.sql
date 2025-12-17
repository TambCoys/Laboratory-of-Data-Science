USE [Group_ID_4_DB];
GO

IF OBJECT_ID('dbo.PublishedSong_Fact', 'U') IS NOT NULL 
    DROP TABLE dbo.PublishedSong_Fact;
GO

CREATE TABLE dbo.PublishedSong_Fact (
    Artist_Code_FK   INT NOT NULL,   
    Album_Code_FK    INT NOT NULL,   
    Date_Code_FK     INT NOT NULL,   
    Symphony_Code_FK INT NOT NULL,   
    Text_Code_FK     INT NOT NULL,
    Feats_Code_FK    INT NOT NULL,   


    Track_ID         VARCHAR(100) NOT NULL, 


    Title            NVARCHAR(255) NOT NULL, 
    Duration_Sec     BIGINT        NULL,
    Streams_First_Month BIGINT     NULL,
    Popularity       INT           NULL,
    Category	     VARCHAR(20)   NOT NULL,

    CONSTRAINT PK_Fact PRIMARY KEY (Artist_Code_FK, Album_Code_FK, Date_Code_FK, Symphony_Code_FK, Text_Code_FK, Feats_Code_FK)
);
GO

-- VINCOLI DI FOREIGN KEY--

ALTER TABLE dbo.PublishedSong_Fact
ADD CONSTRAINT FK_Fact_Artist
    FOREIGN KEY (Artist_Code_FK)
    REFERENCES dbo.Dim_Artist(Artist_Code_PK);
GO

ALTER TABLE dbo.PublishedSong_Fact
ADD CONSTRAINT FK_Fact_Album
    FOREIGN KEY (Album_Code_FK)
    REFERENCES dbo.Dim_Album(Album_Code_PK);
GO

ALTER TABLE dbo.PublishedSong_Fact
ADD CONSTRAINT FK_Fact_Date
    FOREIGN KEY (Date_Code_FK)
    REFERENCES dbo.Dim_Date(Date_Code_PK);
GO

ALTER TABLE dbo.PublishedSong_Fact
ADD CONSTRAINT FK_Fact_Symphony
    FOREIGN KEY (Symphony_Code_FK)
    REFERENCES dbo.Dim_Symphony(Symphony_Code_PK);
GO

ALTER TABLE dbo.PublishedSong_Fact
ADD CONSTRAINT FK_Fact_Text
    FOREIGN KEY (Text_Code_FK)
    REFERENCES dbo.Dim_Text(Text_Code_PK);
GO

ALTER TABLE dbo.PublishedSong_Fact
ADD CONSTRAINT FK_Fact_Feats
    FOREIGN KEY (Feats_Code_FK)
    REFERENCES dbo.Dim_Feats(Feats_Code_PK);
GO
