rule all:
    input:
        "reports/summary.txt",
        "reports/summary_figure.png"

# Step 1: Clean messy_samples.csv
rule clean_samples:
    input:
        data="data/messy_samples.csv",
        script="scripts/clean_up_samples_regex.py"
    output:
        "results/cleaned_samples.csv"
    shell:
        "python {input.script}"

# Step 2: Build the patient feature table
rule build_patient_features:
    input:
        database="data/cohort.db",
        gene_query="sql_queries/query_1.sql",
        patient_query="sql_queries/query_3.sql",
        script="feature_table/build_feature_table.py"
    output:
        "results/patient_feature_table.tsv"
    shell:
        "python {input.script}"

# Step 3: Create report summary (simple figure and text summary)
rule generate_summary:
    input:
        samples="results/cleaned_samples.csv",
        features="results/patient_feature_table.tsv",
        script="reports/generate_summary.py"
    output:
        summary="reports/summary.txt",
        figure="reports/summary_figure.png"
    shell:
        "python {input.script}"
