--- 9)

WITH s_table AS (SELECT AG.Region, COUNT(*) as TotSummer, SUM(PSF.Streams_First_Month) as StreamsSummer
	FROM dbo.PublishedSong_Fact PSF, dbo.Dim_Artist A, dbo.Dim_Artist_Geography AG, dbo.Dim_Date D
	WHERE PSF.Artist_Code_FK=A.Artist_Code_PK AND A.Artist_Geo_Code_FK=AG.Artist_Geo_Code_PK AND PSF.Date_Code_FK=D.Date_Code_PK
		AND D.Season='Summer' 
	GROUP BY AG.Region),
     w_table AS (SELECT AG.Region, COUNT(*) as TotWinter, SUM(PSF.Streams_First_Month) as StreamsWinter
	FROM dbo.PublishedSong_Fact PSF, dbo.Dim_Artist A, dbo.Dim_Artist_Geography AG, dbo.Dim_Date D
	WHERE PSF.Artist_Code_FK=A.Artist_Code_PK AND A.Artist_Geo_Code_FK=AG.Artist_Geo_Code_PK AND PSF.Date_Code_FK=D.Date_Code_PK
		AND D.Season='Winter' 
	GROUP BY AG.Region)
SELECT s.Region, CASE WHEN w.TotWinter!=0 THEN s.TotSummer*1.0/w.TotWinter ELSE NULL END as SummerWinterScore, 
	CASE WHEN w.StreamsWinter!=0 THEN s.StreamsSummer*1.0/w.StreamsWinter ELSE NULL END as SummerWinterStreamsScore
FROM s_table s
FULL OUTER JOIN w_table w ON s.Region=w.Region