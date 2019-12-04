UPDATE FFValMarkup SET
	Annotation = 'В этом задании два лица принадлежат одному человеку.',
	UsedIn = 'training'
WHERE TaskId IN (
	SELECT TOP 8 TaskId FROM FFValMarkup WHERE Doubt = 0 AND Error = 0 AND Result = 1 ORDER BY TaskId
)
UPDATE FFValMarkup SET
	Annotation = 'В этом задании два лица принадлежат разным людям.',
	UsedIn = 'training'
WHERE TaskId IN (
	SELECT TOP 8 TaskId FROM FFValMarkup WHERE Doubt = 0 AND Error = 0 AND Result = 0 ORDER BY TaskId
)
UPDATE FFValMarkup SET
	Annotation = 'Это сложное задание. Два указанных лица принадлежат одному человеку.',
	UsedIn = 'training'
WHERE TaskId IN (
	SELECT TOP 2 TaskId FROM FFValMarkup WHERE Doubt = 1 AND Error = 1 AND Result = 1 ORDER BY TaskId
)
UPDATE FFValMarkup SET
	Annotation = 'Это сложное задание. Два указанных лица принадлежат разным людям.',
	UsedIn = 'training'
WHERE TaskId IN (
	SELECT TOP 2 TaskId FROM FFValMarkup WHERE Doubt = 1 AND Error = 1 AND Result = 0 ORDER BY TaskId
)

UPDATE FFValMarkup SET
	UsedIn = 'exam'
WHERE TaskId IN (
	SELECT TOP 295 TaskId FROM FFValMarkup WHERE Doubt = 0 AND Error = 0 AND Result = 1 AND UsedIn IS NULL ORDER BY TaskId
) OR TaskId IN (
	SELECT TOP 295 TaskId FROM FFValMarkup WHERE Doubt = 0 AND Error = 0 AND Result = 0 AND UsedIn IS NULL ORDER BY TaskId
) OR TaskId IN (
	SELECT TOP 5 TaskId FROM FFValMarkup WHERE Doubt = 1 AND Error = 1 AND Result = 1 AND UsedIn IS NULL ORDER BY TaskId
) OR TaskId IN (
	SELECT TOP 5 TaskId FROM FFValMarkup WHERE Doubt = 1 AND Error = 1 AND Result = 0 AND UsedIn IS NULL ORDER BY TaskId
)
