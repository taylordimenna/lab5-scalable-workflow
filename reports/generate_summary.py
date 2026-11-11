from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

#Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_PATH = PROJECT_ROOT / "results" / "cleaned_samples.csv"
FEATURES_PATH = PROJECT_ROOT / "results" / "patient_feature_table.tsv"
REPORT_DIR = PROJECT_ROOT / "reports"
SUMMARY_PATH = REPORT_DIR / "summary.txt"
FIGURE_PATH = REPORT_DIR / "summary_figure.png"

def main():
    samples = pd.read_csv(SAMPLES_PATH)
    features = pd.read_csv(FEATURES_PATH, sep="\t")

    # Summarize cleaned samples csv
    sample_summary = {
        "Number of sample records": len(samples),
        "Unique sample IDs": samples["sample_id"].nunique(),
        "Missing sex values": samples["sex"].isna().sum(),
        "Asterisk-flagged glucose values": (
            samples["glucose_flag"].eq("asterisk").sum()
        ),
    }

    site_counts = samples["enrollment_site"].value_counts().sort_index()

    # Summarize patient feature table
    patient_summary = {
        "Number of patients": len(features),
        "Unique patient IDs": features["patient_id"].nunique(),
        "Patients missing sex": features["sex"].isna().sum(),
        "Patients missing age": features["age_at_diagnosis"].isna().sum(),
        "Patients missing stage": features["stage"].isna().sum(),
    }

    stage_counts = (
        features["stage"]
        .fillna("Missing")
        .value_counts()
        .sort_index()
    )

    # Write summary
    with SUMMARY_PATH.open("w", encoding="utf-8") as report:
        report.write("Lab 5 Summary:\n")
        report.write(" \n")

        report.write("Cleaned Samples CSV-\n")
        for label, value in sample_summary.items():
            report.write(f"{label}: {value}\n")

        report.write("\nEnrollment site counts:\n")
        for site, count in site_counts.items():
            report.write(f"{site}: {count}\n")

        report.write(" \n")
        report.write("\nPatient Feature Table-\n")
        for label, value in patient_summary.items():
            report.write(f"{label}: {value}\n")

        report.write("\nPatient counts by tumor stage:\n")
        for stage, count in stage_counts.items():
            report.write(f"{stage}: {count}\n")

    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    site_counts.plot(
        kind="bar",
        ax=axes[0],
        title="Samples by Enrollment Site",
    )
    axes[0].set_xlabel("Enrollment Site")
    axes[0].set_ylabel("Number of Samples")
    axes[0].tick_params(axis="x", rotation=0)

    stage_counts.plot(
        kind="bar",
        ax=axes[1],
        title="Patients by Tumor Stage",
    )
    axes[1].set_xlabel("Tumor Stage")
    axes[1].set_ylabel("Number of Patients")
    axes[1].tick_params(axis="x", rotation=45)

    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=300)
    plt.close(fig)

    print("Summary report created successfully.")
    print("Text report:", SUMMARY_PATH)
    print("Figure:", FIGURE_PATH)

if __name__ == "__main__":
    main()
