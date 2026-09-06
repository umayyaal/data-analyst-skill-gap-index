import sqlite3
import pandas as pd
import numpy as np
from datetime import date

DB_PATH = "db/jobs.db"

# Currency conversion rates (static snapshot — update periodically if desired)
INR_TO_USD = 0.0105
GBP_TO_USD = 1.3610


def main():
    conn = sqlite3.connect(DB_PATH)

    jobs_df = pd.read_sql_query("SELECT * FROM jobs;", conn)
    skills_df = pd.read_sql_query("SELECT * FROM job_skills;", conn)

    # datetime conversion
    jobs_df["created"] = pd.to_datetime(jobs_df["created"])

    # currency normalization
    jobs_df["avg_salary_usd"] = np.where(
        jobs_df["country"] == "India", jobs_df["avg_salary"] * INR_TO_USD,
        np.where(jobs_df["country"] == "United Kingdom", jobs_df["avg_salary"] * GBP_TO_USD,
                 jobs_df["avg_salary"])
    )

    # missingness flag
    jobs_df["salary_missing"] = jobs_df["avg_salary"].isna()

    conn.close()
    
    jobs_df["data_extracted_date"] = date.today().isoformat()

    jobs_df.to_csv("dashboard/jobs.csv", index=False)
    skills_df.to_csv("dashboard/jobs_skills.csv", index=False)
    print(f"Exported {len(jobs_df)} jobs and {len(skills_df)} job-skill pairs to dashboard/")


if __name__ == "__main__":
    main()