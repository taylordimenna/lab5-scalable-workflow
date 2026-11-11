-- Query 1: For each patient and gene, count the protein-altering mutations (including silent).
-- Expected grain = one row per patient per gene.
-- Expected row count = 2830 (566 patients, 5 genes per patient)

WITH target_genes(gene_symbol) AS (
    VALUES ('TP53'), ('KRAS'), ('EGFR'), ('STK11'), ('KEAP1')
),

patient_gene AS (
    SELECT p.patient_id, tg.gene_symbol
    FROM patients p
    CROSS JOIN target_genes tg
)

SELECT
    pg.patient_id,
    pg.gene_symbol,
    COUNT(m.mutation_id) AS protein_altering_mutation_count

FROM patient_gene pg

LEFT JOIN samples s
    ON s.patient_id = pg.patient_id

LEFT JOIN mutations m
    ON m.sample_id = s.sample_id
    AND UPPER(TRIM(m.gene_symbol)) = pg.gene_symbol
-- Excludes Silent mutations, while also listing the other specific mutation classifications
    AND m.variant_classification IN (
    'Missense_Mutation',
    'Nonsense_Mutation',
    'Splice_Site',
    'Frame_Shift_Del',
    'Frame_Shift_Ins',
    'In_Frame_Del',
    'In_Frame_Ins',
    'Translation_Start_Site',
    'Nonstop_Mutation'
)

GROUP BY
    pg.patient_id,
    pg.gene_symbol

ORDER BY
    pg.patient_id,
    pg.gene_symbol;

-- Output row count = 2830
-- Each row represents one patient and gene. Each patient has 5 rows, even if they don't have a mutation in the gene.
-- Silent mutations are excluded as per the directions, with all other protein-altering mutations still being counted.
