--- 8) (both answers are correct)

WITH tmp AS (SELECT PSF.ArtistCodeFK, D.Year, COUNT(*) as TotSongsPublished
	FROM Published_song_fact PSF, Date_Dim D
	WHERE PSF.DateCodeFK=D.DateCodePK
	GROUP BY PSF.ArtistCodeFK, D.Year)
SELECT tmp.Year, A.Name, tmp.TotSongsPublished
FROM tmp, Artist_Dim A
WHERE tmp.ArtistCodeFK=A.ArtistCodePK
ORDER BY tmp.Year, tmp.TotSongsPublished DESC

SELECT D.Year, A.Name, COUNT(*) as TotSongsPublished
FROM Published_song_fact PSF, Date_Dim D, Artist_Dim A
WHERE PSF.DateCodeFK=D.DateCodePK AND PSF.ArtistCodeFK=A.ArtistCodePK
GROUP BY A.ArtistCodePK, A.Name, D.Year
ORDER BY D.Year, COUNT(*) DESC

--- 9)

WITH s_table AS (SELECT AG.Region, COUNT(*) as TotSummer, SUM(PSF.streams_1month) as StreamsSummer
	FROM Published_song_fact PSF, Artist_Dim A, Artist_Geo_Dim AG, Date_Dim D
	WHERE PSF.ArtistCodeFK=A.ArtistCodePK AND A.ArtistGeoCodeFK=AG.ArtistGeoCodePK AND PSF.DateCodeFK=D.DateCodePK
		AND D.Season="Summer" 
	GROUP BY AG.Region),
     w_table AS (SELECT AG.Region, COUNT(*) as TotWinter, SUM(PSF.streams_1month) as StreamsWinter
	FROM Published_song_fact PSF, Artist_Dim A, Artist_Geo_Dim AG, Date_Dim D
	WHERE PSF.ArtistCodeFK=A.ArtistCodePK AND A.ArtistGeoCodeFK=AG.ArtistGeoCodePK AND PSF.DateCodeFK=D.DateCodePK
		AND D.Season="Winter" 
	GROUP BY AG.Region)
SELECT s.Region, CASE WHEN w.TotWinter!=0 THEN s.TotSummer*1.0/w.TotWinter ELSE NULL END as SummerWinterScore, 
	CASE WHEN w.StreamsWinter!=0 THEN s.StreamsSummer*1.0/w.StreamsWinter ELSE NULL END as SummerWinterStreamsScore
FROM s_table s
FULL OUTER JOIN w_table w ON s.Region=w.Region

--- 10)

WITH tmp AS (SELECT PSF.Category, AG.Region, SUM(PSF.streams_1month) as TotStreams
	FROM Published_song_fact PSF, Artist_Dim A, Artist_Geo_Dim AG
	WHERE PSF.ArtistCodeFK=A.ArtistCodePK AND A.ArtistGeoCodeFK=AG.ArtistGeoCodePK
	GROUP BY PSF.Category, AG.Region),
     tmp2 AS (SELECT tmp.Category, SUM(TotStreams) as CatTotStreams
	FROM tmp
	GROUP BY tmp.Category)
SELECT tmp.Category, tmp.Region,
	CASE WHEN tmp2.CatTotStreams-tmp.TotStreams!=0 THEN tmp.TotStreams/(tmp2.CatTotStreams-tmp.TotStreams) ELSE NULL END as Ratio
FROM tmp, tmp2
WHERE tmp.Category = tmp2.Category

--- 11)

WITH tmp AS (SELECT PSF.ArtistCodeFK, COUNT(*) as TotSongs,
		AVG(PSF.streams_1month) as AvgStreams, STDEV(PSF.streams_1month) as StDevStreams
	FROM Published_song_fact PSF
	GROUP BY PSF.ArtistCodeFK),
     first_songs_list AS (SELECT PSF.ArtistCodeFK, streams_1month --- se provo  fare direttamente la media qui si rompe
	FROM Published_song_fact PSF, Date_Dim D
	WHERE PSF.DateCodeFK=D.DateCodePK AND D.Day IN (SELECT MIN(D.Day) --- seleziona la data delle prime canzoni
							FROM Published_song_fact PSF2, Date_Dim D2
							WHERE PSF2.DateCodeFK=D2.DateCodePK AND PSF2.ArtistCodeFK=PSF.ArtistCodeFK)),
     first_songs AS (SELECT DISTINCT fsl1.ArtistCodeFK, AVG(fsl2.streams_1month) as AvgFirsts --- per ogni artista, media degli altri artisti
	FROM first_songs_list fsl1, first_songs_list fsl2
	WHERE fsl1.ArtistCodeFK<>fsl2.ArtistCodeFK
	GROUP BY fsl1.ArtistCodeFK),
     flops AS (SELECT A.ArtistCodePK, --- view a parte per gestire gli edge cases
		SUM(CASE WHEN TotSongs>1 AND PSF.streams_1month<tmp.AvgStreams-tmp.StDevStreams THEN 1
			WHEN TotSongs=1 AND PSF.streams_1month<fs.AvgFirsts THEN 1
			ELSE 0 END) as FloppingSongs
	FROM tmp, Published_song_fact PSF, Artist_Dim A, first_songs fs
	WHERE tmp.ArtistCodeFK=PSF.ArtistCodeFK AND tmp.ArtistCodeFK=fs.ArtistCodeFK AND PSF.ArtistCodeFK=A.ArtistCodePK
	GROUP BY A.ArtistCodePK),
    trends AS (SELECT A.ArtistCodePK, --- view a parte per gestire gli edge cases
		SUM(CASE WHEN TotSongs>1 AND PSF.streams_1month>tmp.AvgStreams+tmp.StDevStreams THEN 1
			WHEN TotSongs=1 AND PSF.streams_1month>fs.AvgFirsts THEN 1
			ELSE 0 END) as TrendingSongs
	FROM tmp, Published_song_fact PSF, Artist_Dim A, first_songs fs
	WHERE tmp.ArtistCodeFK=PSF.ArtistCodeFK AND tmp.ArtistCodeFK=fs.ArtistCodeFK AND PSF.ArtistCodeFK=A.ArtistCodePK
	GROUP BY A.ArtistCodePK)
SELECT A.ArtistCodePK, A.Name, 100.0*t.TrendingSongs/tmp.TotSongs as TrendingPercentage,
	1.0*(t.TrendingSongs-f.FloppingSongs)/tmp.TotSongs as TrendingFactor
FROM tmp, flops f, trends t, Artist_Dim A
WHERE tmp.ArtistCodeFK=f.ArtistCodeFK AND tmp.ArtistCodeFK=t.ArtistCodeFK AND tmp.ArtistCodeFK=A.ArtistCodePK