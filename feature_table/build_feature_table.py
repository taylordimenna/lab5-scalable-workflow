from pathlib import Path
import sqlite3
import pandas as pd

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_IN = (PROJECT_ROOT / "data" / "cohort.db")
SQL_PATH = (PROJECT_ROOT / "sql_queries")
TABLE_OUT = (PROJECT_ROOT / "feature_table")

# Creates the folder if it doesn't already exist
TABLE_OUT.mkdir(parents=True, exist_ok=True)

# Reads the SQL files
gene_sql = (
    SQL_PATH / "query_1.sql"
).read_text(encoding="utf-8")
patient_sql = (
    SQL_PATH / "query_3.sql"
).read_text(encoding="utf-8")

# Run both at once
with sqlite3.connect(DATA_IN) as connection:
    gene_counts = pd.read_sql_query(gene_sql, connection)
    patient_features = pd.read_sql_query(patient_sql, connection)

target_genes = ["EGFR", "KEAP1", "KRAS", "STK11", "TP53"]
assert len(patient_features) == 566, (
    f"Expected 566 patients, got {len(patient_features)}"
)

assert patient_features["patient_id"].is_unique, (
    "Patient-level query has duplicate IDs"
)

gene_wide = gene_counts.pivot(
    index="patient_id",
    columns="gene_symbol",
    values="protein_altering_mutation_count"
).reset_index()

# Make sure target genes are present
for gene in target_genes:
    assert gene in gene_wide.columns, (
        f"Missing gene column: {gene}"
    )

# Fill missing gene counts with zero (most patients don't have every gene)
gene_wide[target_genes] = gene_wide[target_genes].fillna(0)

# Combine data
feature_table = patient_features.merge(
    gene_wide,
    on="patient_id",
    how="left",
    validate="one_to_one"
)

# Column order
final_columns = [
    "patient_id",
    "sex",
    "age_at_diagnosis",
    "stage",
    "tissue_source_site",
    "tmb_nonsynonymous",
    "EGFR",
    "KEAP1",
    "KRAS",
    "STK11",
    "TP53"
]

feature_table = feature_table[final_columns]

# Validate final table
assert len(feature_table) == 566
assert feature_table["patient_id"].is_unique
assert feature_table[target_genes].notna().all().all()
assert (feature_table[target_genes] >= 0).all().all()

# Save as a TSV
output_path = TABLE_OUT / "patient_feature_table.tsv"

feature_table.to_csv(
    output_path,
    sep="\t",
    index=False
)

# Report validation results
print("Table created")
print("Output:", output_path)
print("Rows:", len(feature_table))
print("Columns:", len(feature_table.columns))
print("Unique patients:", feature_table["patient_id"].nunique())
print("\nMissing values by column:")
print(feature_table.isna().sum())
