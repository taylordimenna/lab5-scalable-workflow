from pathlib import Path
import csv
import re
from datetime import datetime
from collections import Counter

#Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_IN = PROJECT_ROOT / "data" / "messy_samples.csv"
CSV_OUT = PROJECT_ROOT / "results" / "cleaned_samples.csv"

#Regex patterns
patterns = {
    "sample_id": r"[^A-Za-z0-9]",
    "whitespace": r"\s+",
    "glucose_value": r"^\s*(\d+(?:\.\d+)?)\s*(\*?)\s*$",
    "site": r"site([abc])",
}

#Clean sample IDs
def clean_sample_id(value):
    cleaned = re.sub(patterns["sample_id"], "", value.strip())
    return cleaned.upper()

#Clean patient names
def clean_patient_name(value):
    return re.sub(
        patterns["whitespace"], " ", value.strip()
    ).title()

#Clean sex
def clean_sex(value):
    value = value.strip().lower()

    if not value:
        return None

    if value in ("m", "male"):
        return "Male"

    if value in ("f", "female"):
        return "Female"

    if value in ("u", "unknown"):
        return "Unknown"

    return "Unknown"

#Clean enrollment site
def clean_site(value):
    value = value.strip().lower()
    value = re.sub(r"[\s_-]+", "", value)

    match = re.fullmatch(patterns["site"], value)

    if match:
        return f"Site {match.group(1).upper()}"

    return None

#Clean dob
def clean_dob(value):
    value = value.strip()

    if not value:
        return None

    #Four-digit years
    date_formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m.%d.%Y",
        "%d-%b-%Y",
        "%d-%B-%Y",
    ]

    for date_format in date_formats:
        try:
            return datetime.strptime(
                value, date_format
            ).strftime("%Y-%m-%d")

        except ValueError:
            continue

    #Two-digit years
    two_digit_formats = [
        "%m/%d/%y",
        "%m.%d.%y",
        "%d-%b-%y",
    ]

    for date_format in two_digit_formats:
        try:
            parsed = datetime.strptime(value, date_format)
            year = parsed.year

            if year >= 2027:
                year -= 100

            return parsed.replace(
                year=year
            ).strftime("%Y-%m-%d")

        except ValueError:
            continue

    return None

#Clean glucose value
def clean_glucose(value):
    value = value.strip()

    if not value:
        return None, None

    match = re.fullmatch(
        patterns["glucose_value"], value
    )

    if match:
        numeric_value = float(match.group(1))
        flag = "asterisk" if match.group(2) else None

        return numeric_value, flag

    return None, "invalid_value"

#Clean glucose units
def clean_glucose_unit(value):
    value = value.strip().lower()

    units = {
        "mg/dl": "mg/dL",
        "mmol/l": "mmol/L",
    }

    return units.get(value)

#Clean whitespaces
def clean_notes(value):
    value = re.sub(
        patterns["whitespace"], " ", value.strip()
    )

    return value if value else None

#Read and clean CSV
def clean_samples(path):
    required_columns = {
        "sample_id",
        "patient_name",
        "dob",
        "sex",
        "enrollment_site",
        "glucose_value",
        "glucose_unit",
        "notes",
    }

    cleaned_records = []

    with open(
        path, "r", newline="", encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                "Input CSV is missing required columns."
            )

        for row in reader:

            glucose_value, glucose_flag = clean_glucose(
                row["glucose_value"]
            )

            cleaned = {
                "sample_id": clean_sample_id(row["sample_id"]),
                "patient_name": clean_patient_name(row["patient_name"]),
                "dob": clean_dob(row["dob"]),
                "sex": clean_sex(row["sex"]),
                "enrollment_site": clean_site(row["enrollment_site"]),
                "glucose_value": glucose_value,
                "glucose_unit": clean_glucose_unit(row["glucose_unit"]),
                "glucose_flag": glucose_flag,
                "notes": clean_notes(row["notes"]),
            }

            cleaned_records.append(cleaned)

    return cleaned_records

#Check for errors
def validate_samples(records):
    if not records:
        raise ValueError(
            "No records were found in the input CSV."
        )

    sample_ids = [
        row["sample_id"] for row in records
    ]

    if any(not sample_id for sample_id in sample_ids):
        raise ValueError(
            "One or more sample IDs are missing."
        )

    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError(
            "Duplicate sample IDs detected."
        )

    valid_sites = {"Site A", "Site B", "Site C"}

    invalid_sites = [
        row["enrollment_site"]
        for row in records
        if row["enrollment_site"] not in valid_sites
    ]

    if invalid_sites:
        raise ValueError(
            f"Invalid enrollment sites: {invalid_sites}"
        )

#Write CSV file
def write_csv(records, path):
    fieldnames = [
        "sample_id",
        "patient_name",
        "dob",
        "sex",
        "enrollment_site",
        "glucose_value",
        "glucose_unit",
        "glucose_flag",
        "notes",
    ]

    path.parent.mkdir(
        parents=True, exist_ok=True
    )

    with open(
        path, "w", newline="", encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file, fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(records)


#Report results
def report_results(records):
    fieldnames = [
        "sample_id",
        "patient_name",
        "dob",
        "sex",
        "enrollment_site",
        "glucose_value",
        "glucose_unit",
        "glucose_flag",
        "notes",
    ]

    sample_ids = [
        row["sample_id"] for row in records
    ]

    print("\nCleaning summary")

    print(f"Input records: {len(records)}")
    print(f"Output records: {len(records)}")
    print(f"Unique sample IDs: {len(set(sample_ids))}")

    print("\nMissing values:")

    for column in fieldnames:
        missing = sum(
            row[column] is None
            for row in records
        )

        print(f"{column}: {missing}")

    print("\nEnrollment site counts:")

    for site, count in sorted(
        Counter(
            row["enrollment_site"]
            for row in records
        ).items()
    ):
        print(f"{site}: {count}")

    flagged = sum(
        row["glucose_flag"] == "asterisk"
        for row in records
    )

    print(f"\nAsterisk-flagged glucose values: {flagged}")
    print(f"\nOutput file: {CSV_OUT}")
    print("Cleaning completed successfully!")

def main():

    records = clean_samples(CSV_IN)

    validate_samples(records)

    write_csv(records, CSV_OUT)

    report_results(records)


if __name__ == "__main__":
    main()
