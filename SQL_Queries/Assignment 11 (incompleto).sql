--- 11)

WITH tmp AS (SELECT PSF.Artist_Code_FK, COUNT(*) as TotSongs,
		AVG(PSF.Streams_First_Month) as AvgStreams, STDEV(PSF.Streams_First_Month) as StDevStreams
	FROM dbo.PublishedSong_Fact PSF
	GROUP BY PSF.Artist_Code_FK),
     first_song_date AS (SELECT PSF.Artist_Code_FK, MIN(D.Day) as FirstDay
	FROM dbo.PublishedSong_Fact PSF, dbo.Dim_Date D
	WHERE PSF.Date_Code_FK=D.Date_Code_PK
	GROUP BY PSF.Artist_Code_FK),
     first_songs_list AS (SELECT PSF.Artist_Code_FK, Streams_First_Month --- se provo  fare direttamente la media qui si rompe
	FROM dbo.PublishedSong_Fact PSF, first_song_date fsd, dbo.Dim_Date D
	WHERE PSF.Date_Code_FK=D.Date_Code_PK AND PSF.Artist_Code_FK=fsd.Artist_Code_FK AND D.Day=fsd.FirstDay),
     first_songs AS (SELECT DISTINCT fsl1.Artist_Code_FK, AVG(fsl2.Streams_First_Month) as AvgFirsts --- per ogni artista, media degli altri artisti
	FROM first_songs_list fsl1, first_songs_list fsl2
	WHERE fsl1.Artist_Code_FK<>fsl2.Artist_Code_FK
	GROUP BY fsl1.Artist_Code_FK),
     flops AS (SELECT A.Artist_Code_PK, --- view a parte per gestire gli edge cases
		SUM(CASE WHEN TotSongs>1 AND PSF.Streams_First_Month<tmp.AvgStreams-tmp.StDevStreams THEN 1
			WHEN TotSongs=1 AND PSF.Streams_First_Month<fs.AvgFirsts THEN 1
			ELSE 0 END) as FloppingSongs
	FROM tmp, dbo.PublishedSong_Fact PSF, dbo.Dim_Artist A, first_songs fs
	WHERE tmp.Artist_Code_FK=PSF.Artist_Code_FK AND tmp.Artist_Code_FK=fs.Artist_Code_FK AND PSF.Artist_Code_FK=A.Artist_Code_PK
	GROUP BY A.Artist_Code_PK),
    trends AS (SELECT A.Artist_Code_PK, --- view a parte per gestire gli edge cases
		SUM(CASE WHEN TotSongs>1 AND PSF.Streams_First_Month>tmp.AvgStreams+tmp.StDevStreams THEN 1
			WHEN TotSongs=1 AND PSF.Streams_First_Month>fs.AvgFirsts THEN 1
			ELSE 0 END) as TrendingSongs
	FROM tmp, dbo.PublishedSong_Fact PSF, dbo.Dim_Artist A, first_songs fs
	WHERE tmp.Artist_Code_FK=PSF.Artist_Code_FK AND tmp.Artist_Code_FK=fs.Artist_Code_FK AND PSF.Artist_Code_FK=A.Artist_Code_PK
	GROUP BY A.Artist_Code_PK)
SELECT A.Artist_Code_PK, A.Name, 100.0*t.TrendingSongs/tmp.TotSongs as TrendingPercentage,
	1.0*(t.TrendingSongs-f.FloppingSongs)/tmp.TotSongs as TrendingFactor
FROM tmp, flops f, trends t, dbo.Dim_Artist A
WHERE tmp.Artist_Code_FK=f.Artist_Code_FK AND tmp.Artist_Code_FK=t.Artist_Code_FK AND tmp.Artist_Code_FK=A.Artist_Code_PK
