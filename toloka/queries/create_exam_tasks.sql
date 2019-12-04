SET NOCOUNT ON;

DECLARE @date_end date = ?

SELECT DISTINCT Id
INTO #Idx
FROM FindFaceEvents f WITH (nolock)
WHERE
    Store LIKE '107%' AND
    CreatedDate <= @date_end

SELECT DISTINCT
  EventId1, EventId2, Result, Annotation
INTO #Pairs
FROM FFValMarkup
WHERE Annotation IS NOT NULL;


WITH ResultSet AS (
  SELECT DISTINCT * FROM (
    SELECT m.EventId1 EventId1, m.EventId2 EventId2, m.Confidence
    FROM FFMatrix m
      INNER HASH JOIN #Idx i1 WITH (nolock) ON i1.Id=m.EventId1
    UNION ALL
    SELECT m.EventId2 EventId1, m.EventId1 EventId2, m.Confidence
    FROM FFMatrix m
      INNER HASH JOIN #Idx i2 WITH (nolock) ON i2.Id=m.EventId2
  ) rs
  WHERE EventId1 <> EventId2
),

RowNumber AS (
  SELECT
    EventId1,
    EventId2,
    ROW_NUMBER() OVER (PARTITION BY EventId1 ORDER BY Confidence DESC, EventId2) RN
  FROM ResultSet
)

SELECT
  EventId1,
  MAX(CASE WHEN RN = 1 THEN EventId2 END) EventId2,
  MAX(CASE WHEN RN = 2 THEN EventId2 END) EventId3
INTO #Thumbs
FROM RowNumber
GROUP BY EventId1
ORDER BY EventId1


SELECT
  CONCAT(CAST(p.EventId1 AS varchar(max)), '.jpeg') image_left,
  CONCAT(CAST(p.EventId2 AS varchar(max)), '.jpeg') image_right,
  CONCAT(CAST(t1.EventId1 AS varchar(max)), '.jpg') thumb_left1,
  CONCAT(CAST(t1.EventId2 AS varchar(max)), '.jpg') thumb_left2,
  CONCAT(CAST(t1.EventId3 AS varchar(max)), '.jpg') thumb_left3,
  CONCAT(CAST(t2.EventId1 AS varchar(max)), '.jpg') thumb_right1,
  CONCAT(CAST(t2.EventId2 AS varchar(max)), '.jpg') thumb_right2,
  CONCAT(CAST(t2.EventId3 AS varchar(max)), '.jpg') thumb_right3,
  Result result,
  Annotation message_on_unknown_solution
FROM #Pairs p
  INNER HASH JOIN #Thumbs t1 ON t1.EventId1=p.EventId1
  INNER HASH JOIN #Thumbs t2 ON t2.EventId1=p.EventId2
