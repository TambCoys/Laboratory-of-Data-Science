--- 10)

WITH tmp AS (SELECT PSF.Category, AG.Region, SUM(PSF.Streams_First_Month) as TotStreams
	FROM dbo.PublishedSong_Fact PSF, dbo.Dim_Artist A, dbo.Dim_Artist_Geography AG
	WHERE PSF.Artist_Code_FK=A.Artist_Code_PK AND A.Artist_Geo_Code_FK=AG.Artist_Geo_Code_PK
	GROUP BY PSF.Category, AG.Region),
     tmp2 AS (SELECT tmp.Category, SUM(TotStreams) as CatTotStreams
	FROM tmp
	GROUP BY tmp.Category)
SELECT tmp.Category, tmp.Region,
	CASE WHEN tmp2.CatTotStreams-tmp.TotStreams!=0 THEN tmp.TotStreams/(tmp2.CatTotStreams-tmp.TotStreams) ELSE NULL END as Ratio
FROM tmp, tmp2
WHERE tmp.Category = tmp2.Category