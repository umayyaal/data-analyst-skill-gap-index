{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8f214b67-a0b2-4ce1-ad16-1e2c795f44fa",
   "metadata": {},
   "outputs": [],
   "source": [
    "import sqlite3\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "\n",
    "DB_PATH = \"db/jobs.db\"\n",
    "\n",
    "# Currency conversion rates (static snapshot — update periodically if desired)\n",
    "INR_TO_USD = 0.0105\n",
    "GBP_TO_USD = 1.3610\n",
    "\n",
    "\n",
    "def main():\n",
    "    conn = sqlite3.connect(DB_PATH)\n",
    "\n",
    "    jobs_df = pd.read_sql_query(\"SELECT * FROM jobs;\", conn)\n",
    "    skills_df = pd.read_sql_query(\"SELECT * FROM job_skills;\", conn)\n",
    "\n",
    "    # datetime conversion\n",
    "    jobs_df[\"created\"] = pd.to_datetime(jobs_df[\"created\"])\n",
    "\n",
    "    # currency normalization\n",
    "    jobs_df[\"avg_salary_usd\"] = np.where(\n",
    "        jobs_df[\"country\"] == \"India\", jobs_df[\"avg_salary\"] * INR_TO_USD,\n",
    "        np.where(jobs_df[\"country\"] == \"United Kingdom\", jobs_df[\"avg_salary\"] * GBP_TO_USD,\n",
    "                 jobs_df[\"avg_salary\"])\n",
    "    )\n",
    "\n",
    "    # missingness flag\n",
    "    jobs_df[\"salary_missing\"] = jobs_df[\"avg_salary\"].isna()\n",
    "\n",
    "    conn.close()\n",
    "\n",
    "    jobs_df.to_csv(\"dashboard/jobs.csv\", index=False)\n",
    "    skills_df.to_csv(\"dashboard/jobs_skills.csv\", index=False)\n",
    "    print(f\"Exported {len(jobs_df)} jobs and {len(skills_df)} job-skill pairs to dashboard/\")\n",
    "\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    main()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.14.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
