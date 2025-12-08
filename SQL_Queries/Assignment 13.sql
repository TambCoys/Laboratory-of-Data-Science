--- 12) Canzoni trending (in base a popularity) per artista in base e quanti featuring ha rispetto alla media dell'artista

WITH pop AS (SELECT PSF.Artist_Code_FK, AVG(PSF.Popularity) as AvgPopularity, STDEV(PSF.Popularity) as StDevPopularity, COUNT(*) as TotSongs
	FROM dbo.PublishedSong_Fact PSF
	GROUP BY PSF.Artist_Code_FK),
     feats AS (SELECT FB.Feats_Code_FK, COUNT(*) as NFeats
	FROM dbo.Feats_Bridge FB
	GROUP BY FB.Feats_Code_FK)
     total_feats AS (SELECT PSF.Artist_Code_FK, COUNT(FB.Feat_Artist_Code_FK) as TotFeats
	FROM dbo.PublishedSong_Fact PSF, dbo.Feats_Bridge FB
	WHERE PSF.Feats_Code_FK=FB.Feats_Code_FK
	GROUP BY PSF.Artist_Code_FK)
SELECT A.Name, PSF.Name, feats.NFeats, 
	CASE WHEN feats.Nfeats IS NOT NULL THEN feats.NFeats-(tf.TotFeats/pop.TotSongs) ELSE 0 END as DeltaFeats
FROM pop, dbo.Dim_Artist A, total_feats tf, dbo.PublishedSong_Fact PSF
LEFT JOIN feats ON PSF.Feats_Code_FK=feats.Feats_Code_FK 
WHERE pop.Artist_Code_FK=PSF.Artist_Code_FK AND PSF.Artist_Code_FK=A.Artist_Code_PK AND tf.Artist_Code_FK=PSF.Artist_Code_FK
	AND PSF.Popularity>AvgPopularity+StDevPopularity
