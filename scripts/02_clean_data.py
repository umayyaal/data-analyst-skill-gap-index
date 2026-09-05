import os
import json
import glob
import re
import pandas as pd

RAW_DATA_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

# Map filename prefix -> country name
COUNTRY_MAP = {"in": "India", "us": "United States", "gb": "United Kingdom"}

# Skills we're going to look for inside job descriptions + titles.
# Keys = clean display name, Values = regex pattern to search for (case-insensitive)
SKILL_PATTERNS = {
    "SQL": r"\bsql\b",
    "Python": r"\bpython\b",
    "Power BI": r"power\s?bi",
    "Tableau": r"\btableau\b",
    "Excel": r"\bexcel\b",
    "R": r"\br\b(?!\w)",              # tricky: standalone "R", avoid matching inside other words
    "SAS": r"\bsas\b",
    "VBA": r"\bvba\b",
    "AWS": r"\baws\b",
    "Azure": r"\bazure\b",
    "Machine Learning": r"machine\s?learning",
    "Statistics": r"\bstatistic",
    "Looker": r"\blooker\b",
    "Alteryx": r"\balteryx\b",
    "Google Analytics": r"google\s?analytics",
    "ETL": r"\betl\b",
    "Big Query": r"big\s?query",
    "Spark": r"\bspark\b",
}


def load_all_raw_files():
    """Read every raw JSON file and combine into one list of job records."""
    all_jobs = []
    files = glob.glob(f"{RAW_DATA_DIR}/*.json")
    for filepath in files:
        filename = os.path.basename(filepath)
        country_code = filename.split("_")[0]  # e.g. "in_page1_20260808.json" -> "in"
        country_name = COUNTRY_MAP.get(country_code, "Unknown")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for job in data.get("results", []):
            job["country"] = country_name
            all_jobs.append(job)
    return all_jobs


def extract_skills(text):
    """Given a text string, return a list of matched skills."""
    if not text:
        return []
    text_lower = text.lower()
    found = [skill for skill, pattern in SKILL_PATTERNS.items()
             if re.search(pattern, text_lower)]
    return found


def build_clean_dataframe(jobs):
    """Turn raw job dicts into a clean, flat pandas DataFrame."""
    rows = []
    for job in jobs:
        title = job.get("title", "")
        description = job.get("description", "")
        combined_text = f"{title} {description}"

        rows.append({
            "job_id": job.get("id"),
            "title": title,
            "company": job.get("company", {}).get("display_name", "Unknown"),
            "location": job.get("location", {}).get("display_name", "Unknown"),
            "country": job.get("country"),
            "category": job.get("category", {}).get("label", "Unknown"),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "salary_is_predicted": job.get("salary_is_predicted", "0") == "1",
            "contract_time": job.get("contract_time", "Unknown"),
            "created": job.get("created"),
            "description": description,
            "skills": extract_skills(combined_text),
            "num_skills": len(extract_skills(combined_text)),
        })

    df = pd.DataFrame(rows)

    # basic cleaning
    df["created"] = pd.to_datetime(df["created"], errors="coerce")
    df["avg_salary"] = df[["salary_min", "salary_max"]].mean(axis=1)
    df = df.drop_duplicates(subset=["job_id"])  # in case of overlap across pages

    return df


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print("Loading raw files...")
    jobs = load_all_raw_files()
    print(f"Loaded {len(jobs)} raw job records")

    print("Cleaning + extracting skills...")
    df = build_clean_dataframe(jobs)

    output_path = f"{PROCESSED_DIR}/jobs_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned data: {output_path}")
    print(f"Final row count: {len(df)}")
    print(f"\nSample skill extraction:\n{df[['title', 'skills']].head(5)}")


if __name__ == "__main__":
    main()