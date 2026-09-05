import sqlite3
import pandas as pd
import ast

CSV_PATH = "data/processed/jobs_clean.csv"
DB_PATH = "db/jobs.db"


def load_dataframe():
    df = pd.read_csv(CSV_PATH)
    # "skills" was saved as a string like "['SQL', 'Power BI']" — convert back to a real list
    df["skills"] = df["skills"].apply(ast.literal_eval)
    return df


def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        title TEXT,
        company TEXT,
        location TEXT,
        country TEXT,
        category TEXT,
        salary_min REAL,
        salary_max REAL,
        avg_salary REAL,
        salary_is_predicted INTEGER,
        contract_time TEXT,
        created TEXT,
        num_skills INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_skills (
        job_id TEXT,
        skill TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
    )
    """)

    conn.commit()


def insert_data(conn, df):
    cursor = conn.cursor()

    # Insert into jobs table (one row per job)
    jobs_df = df.drop(columns=["skills", "description"])
    jobs_df.to_sql("jobs", conn, if_exists="replace", index=False)

    # Insert into job_skills table (one row per job-skill pair — a proper normalized table)
    skill_rows = []
    for _, row in df.iterrows():
        for skill in row["skills"]:
            skill_rows.append({"job_id": row["job_id"], "skill": skill})

    skills_df = pd.DataFrame(skill_rows)
    skills_df.to_sql("job_skills", conn, if_exists="replace", index=False)

    conn.commit()
    print(f"Inserted {len(jobs_df)} jobs and {len(skills_df)} job-skill pairs")


def main():
    df = load_dataframe()
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    insert_data(conn, df)
    conn.close()
    print(f"Database ready at {DB_PATH}")


if __name__ == "__main__":
    main()