# AI Usage within ```Snakefile```
## Model used
ChatGPT (GPT-5.6 Luna)

## Error
I wasn't able to get my Snakefile to reproduce the output files (```cleaned_samples.csv```, ```patient_feature_table.tsv```, ```summary.txt```, and ```summary_figure.png```).

When I ran:

    snakemake -n

to do a dry run and see how well my work could be reproduced, this was returned in the terminal:

    "Building DAG of jobs...
    Job stats:
    job                       count
    ----------------------  -------
    build_patient_features        1
    clean_samples                 1
    generate_summary              1
    all                           1
    total                         4


    [Wed Nov 11 18:21:03 2026]
    rule build_patient_features:
        input: data/cohort.db, sql_queries/query_1.sql, sql_queries/query_3.sql
        output: results/patient_feature_table.tsv
        jobid: 3
        reason: Missing output files: results/patient_feature_table.tsv
        resources: tmpdir=/tmp
    [Wed Nov 11 18:21:03 2026]
    rule clean_samples:
        input: data/messy_samples.csv
        output: results/cleaned_samples.csv
        jobid: 2
        reason: Missing output files: results/cleaned_samples.csv
        resources: tmpdir=/tmp
    [Wed Nov 11 18:21:03 2026]
    rule generate_summary:
        input: results/cleaned_samples.csv, results/patient_feature_table.tsv
        output: reports/summary.txt, reports/summary_figure.png
        jobid: 1
        reason: Missing output files: reports/summary_figure.png, reports/summary.txt; Input files updated by another job: results/patient_feature_table.tsv, results/cleaned_samples.csv
        resources: tmpdir=/tmp
    [Wed Nov 11 18:21:03 2026]
    rule all:
        input: reports/summary.txt, reports/summary_figure.png
        jobid: 0
        reason: Input files updated by another job: reports/summary_figure.png, reports/summary.txt
        resources: tmpdir=/tmp
    Job stats:
    job                       count
    ----------------------  -------
    build_patient_features        1
    clean_samples                 1
    generate_summary              1
    all                           1
    total                         4

    Reasons:
        (check individual jobs above for details)
        input files updated by another job:
            all, generate_summary
        output files have to be generated:
            build_patient_features, clean_samples, generate_summary
    This was a dry-run (flag -n). The order of jobs does not reflect the order of execution."

## What this error means
This indicates that ```cleaned_samples.csv```, ```patient_feature_table.tsv```, ```summary.txt```, and ```summary_figure.png``` would not be reproduced with the current state of ```Snakefile```.

## Existing script
The problematic portions of my Snakefile were the 'shell' parts of each rule. The existing script for each rule was:

    shell:
            "python scripts/clean_up_samples_regex.py --input {input} --output {output}"

    shell:
            "python feature_table/build_feature_table.py --input {input} --output {output}"

    shell:
            "python reports/generate_summary.py --input {input} --output {output}"

Since I was modeling these after the demo snakefile within ```week10-workflow-management```, I assumed that the problem was with the {input} and {output} portions of the script.

## Prompt
The prompt I typed into the LLM to allow me to correct this was:

    "I am writing a Snakefile for a lab in my applied computing class. When I ran snakemake -n to do a dry run of it, I wasn't able to get it to remake the files. I believe I have a problem with the input and output sections of the shell compounds of the snakefile. What do I need to change in my snakefile to get this to run correctly? Please only suggest changes to my snakefile, unless I need to change my other scripts. Only include what parts I need to change, do not add extra information.
    
    For reference here is my snakefile:
    (Pasted entire snakefile here)
    
    Here is one of the scripts used: 
    (Pasted entire script here)"

## Output
The output given to me by the LLM was:

    "Change the ```input``` and ```output``` arguments in the shell commands to explicitly reference the named files.

    1. ```build_patient_features```

    Replace:
        rule build_patient_features:
            input:
                database="data/cohort.db",
                gene_query="sql_queries/query_1.sql",
                patient_query="sql_queries/query_3.sql",
            output:
                "results/patient_feature_table.tsv"    
            shell:
                "python feature_table/build_feature_table.py --input {input} --output {output}"

    With:
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

    Your script already defines the input database, SQL files, and output path internally, so it does not accept ```--input``` or ```--output``` arguments.

    2. ```generate_summary```

    If script contents have the same form, replace:
        rule generate_summary:
            input:
                samples="results/cleaned_samples.csv",
                features="results/patient_feature_table.tsv",
            output:
                summary="reports/summary.txt",
                figure="reports/summary_figure.png"
            shell:
                "python reports/generate_summary.py --input {input} --output {output}"

    With:
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

    3. ```clean_samples```

    If script contents have the same form, replace:
        rule clean_samples:
            input:
                data="data/messy_samples.csv",
            output:
                "results/cleaned_samples.csv"
            shell:
                "python scripts/clean_up_samples_regex.py --input {input} --output {output}"

    With:
        rule clean_samples:
        input:
            data="data/messy_samples.csv",
            script="scripts/clean_up_samples_regex.py"
        output:
            "results/cleaned_samples.csv"
        shell:
            "python {input.script}"


## Verifying the fix
To verify the fix, I made the change to my script and then ran:

    snakemake -n

again to run another dry run. I was able to see in the terminal that all four of these files would be reproduced, so I decided to keep the fix.