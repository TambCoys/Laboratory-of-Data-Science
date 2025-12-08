-- 6. Dim_Text_SSIS
IF OBJECT_ID('dbo.Dim_Text_SSIS') IS NOT NULL
    DROP TABLE dbo.Dim_Text_SSIS;
GO

CREATE TABLE dbo.Dim_Text_SSIS (
    Text_Code_PK       INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    N_Swear_Words_IT   INT        NULL,
    N_Swear_Words_EN   INT        NULL,
    Is_Explicit        BIT        NULL,
    Lyrics             NVARCHAR(MAX) NULL
);
GO
