-- 5. Dim_Text_Category (lyrics – da Assignment 3)
IF OBJECT_ID('dbo.Dim_Text') IS NOT NULL DROP TABLE Dim_Text;
CREATE TABLE dbo.Dim_Text (
    Text_Code_PK             VARCHAR(10) IDENTITY(1,1) NOT NULL PRIMARY KEY,
    N_Swear_Words_IT         INT    NULL,   
    N_Swear_Words_EN         INT    NULL,  
    Is_Explicit              BIT    NULL,  
    Lyrics                   NVARCHAR(2000) NULL
);
