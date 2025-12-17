--- 8) (anche 8bis risolve questa query)

SELECT D.Year, A.Name, COUNT(*) as TotSongsPublished
FROM dbo.PublishedSong_Fact PSF, dbo.Dim_Date D, dbo.Dim_Artist A
WHERE PSF.Date_Code_FK=D.Date_Code_PK AND PSF.Artist_Code_FK=A.Artist_Code_PK
GROUP BY A.Artist_Code_PK, A.Name, D.Year
ORDER BY D.Year, COUNT(*) DESC
