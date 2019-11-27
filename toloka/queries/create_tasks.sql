SET NOCOUNT ON;

DECLARE @date_start date = ?
DECLARE @date_end date = ?
DECLARE @camera int = ?
DECLARE @threshold numeric(15, 4) = ?
DECLARE @min_quality numeric(15, 4) = ?
DECLARE @top_limit int = ?

SELECT DISTINCT Id
INTO #Idx
FROM FindFaceEvents f WITH (nolock)
WHERE
    Store LIKE '107%' AND
    CreatedDate BETWEEN @date_start AND @date_end AND
    (@camera IS NULL OR (@camera IS NOT NULL AND Camera = @camera)) AND
    Quality >= @min_quality;

WITH ResultSet AS (
  SELECT DISTINCT * FROM (
    SELECT m.EventId1 EventId1, m.EventId2 EventId2, m.Confidence
    FROM FFMatrix m
      INNER HASH JOIN #Idx i1 WITH (nolock) ON i1.Id=m.EventId1
      INNER HASH JOIN #Idx i2 WITH (nolock) ON i2.Id=m.EventId2

    UNION ALL

    SELECT m.EventId2 EventId1, m.EventId1 EventId2, m.Confidence
    FROM FFMatrix m
      INNER HASH JOIN #Idx i1 WITH (nolock) ON i1.Id=m.EventId1
      INNER HASH JOIN #Idx i2 WITH (nolock) ON i2.Id=m.EventId2
  ) rs
  WHERE EventId1 <> EventId2
)

SELECT
  EventId1,
  EventId2,
  Confidence,
  ROW_NUMBER() OVER (PARTITION BY EventId1 ORDER BY Confidence DESC, EventId2) RN
INTO #FullTaskMatrix
FROM ResultSet

SELECT
  EventId1,
  MAX(CASE WHEN RN = 1 THEN EventId2 END) EventId2,
  MAX(CASE WHEN RN = 2 THEN EventId2 END) EventId3
INTO #Thumbs
FROM #FullTaskMatrix
GROUP BY EventId1
ORDER BY EventId1


SELECT DISTINCT
  IIF(EventId1 > EventId2, EventId1, EventId2) EventId1,
  IIF(EventId1 > EventId2, EventId2, EventId1) EventId2
INTO #Pairs
FROM #FullTaskMatrix
WHERE Confidence < @threshold AND RN <= @top_limit


SELECT
  CONCAT(CAST(p.EventId1 AS varchar(max)), '.jpeg') image_left,
  CONCAT(CAST(p.EventId2 AS varchar(max)), '.jpeg') image_right,
  CONCAT(CAST(t1.EventId1 AS varchar(max)), '.jpg') thumb_left1,
  CONCAT(CAST(t1.EventId2 AS varchar(max)), '.jpg') thumb_left2,
  CONCAT(CAST(t1.EventId3 AS varchar(max)), '.jpg') thumb_left3,
  CONCAT(CAST(t2.EventId1 AS varchar(max)), '.jpg') thumb_right1,
  CONCAT(CAST(t2.EventId2 AS varchar(max)), '.jpg') thumb_right2,
  CONCAT(CAST(t2.EventId3 AS varchar(max)), '.jpg') thumb_right3
FROM #Pairs p
  INNER HASH JOIN #Thumbs t1 ON t1.EventId1=p.EventId1
  INNER HASH JOIN #Thumbs t2 ON t2.EventId1=p.EventId2
