--- 8bis) (anche 8 risolve questa query)

WITH tmp AS (SELECT PSF.Artist_Code_FK, D.Year, COUNT(*) as TotSongsPublished
	FROM dbo.PublishedSong_Fact PSF, dbo.Dim_Date D
	WHERE PSF.Date_Code_FK=D.Date_Code_PK
	GROUP BY PSF.Artist_Code_FK, D.Year)
SELECT tmp.Year, A.Name, tmp.TotSongsPublished
FROM tmp, dbo.Dim_Artist A
WHERE tmp.Artist_Code_FK=A.Artist_Code_PK
ORDER BY tmp.Year, tmp.TotSongsPublished DESC
