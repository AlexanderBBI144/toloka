SET NOCOUNT ON;

SELECT Id, Face, Frame
INTO #Ids
FROM FindFaceEvents f WITH (nolock)
WHERE CreatedDate BETWEEN '2019-09-12' AND '2019-09-13' AND Store LIKE '107%'


SELECT TOP 10
	CONCAT(CAST(EventId1 AS varchar(max)), '.jpeg') image_left,
	CONCAT(CAST(EventId2 AS varchar(max)), '.jpeg') image_right,
	CONCAT(CAST(EventId1 AS varchar(max)), '.jpg') thumb_left1,
	CONCAT(CAST(EventId1 AS varchar(max)), '.jpg') thumb_left2,
	CONCAT(CAST(EventId1 AS varchar(max)), '.jpg') thumb_left3,
	CONCAT(CAST(EventId2 AS varchar(max)), '.jpg') thumb_right1,
	CONCAT(CAST(EventId2 AS varchar(max)), '.jpg') thumb_right2,
	CONCAT(CAST(EventId2 AS varchar(max)), '.jpg') thumb_right3,
	NULL result,
	NULL message_on_unknown_solution
FROM FFMatrix m WITH (nolock)
	JOIN #Ids i1 ON m.EventId1=i1.Id
	JOIN #Ids i2 ON m.EventId2=i2.Id
UNION ALL
SELECT TOP 2
	CONCAT(CAST(EventId1 AS varchar(max)), '.jpeg') image_left,
	CONCAT(CAST(EventId2 AS varchar(max)), '.jpeg') image_right,
	CONCAT(CAST(EventId1 AS varchar(max)), '.jpg') thumb_left1,
	CONCAT(CAST(EventId1 AS varchar(max)), '.jpg') thumb_left2,
	CONCAT(CAST(EventId1 AS varchar(max)), '.jpg') thumb_left3,
	CONCAT(CAST(EventId2 AS varchar(max)), '.jpg') thumb_right1,
	CONCAT(CAST(EventId2 AS varchar(max)), '.jpg') thumb_right2,
	CONCAT(CAST(EventId2 AS varchar(max)), '.jpg') thumb_right3,
	NULL result,
	NULL message_on_unknown_solution
FROM FFMatrix m WITH (nolock)
	JOIN #Ids i1 ON m.EventId1=i1.Id
	JOIN #Ids i2 ON m.EventId2=i2.Id
