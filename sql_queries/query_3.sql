-- Query 3: Get patient level clinical and sample features.
-- Expected grain = one row per patient
-- Expected row count = 566

SELECT
    p.patient_id,
    p.sex,
    p.age_at_diagnosis,
    p.stage,
    s.tissue_source_site,
    s.tmb_nonsynonymous

FROM patients p

LEFT JOIN samples s
    ON s.patient_id = p.patient_id

ORDER BY
    p.patient_id;

-- Output row count = 566
-- Each row represents a different patient.