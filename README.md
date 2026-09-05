# 📊 Data Analyst Skill Gap Index — Python + SQL + Power BI

## 📖 Project Overview

This project analyzes live "Data Analyst" job postings pulled directly from the 
Adzuna Jobs API across three markets — India, the United States, and the United 
Kingdom — to answer a question every job seeker actually has: **what do employers 
really want, and what does it pay?**

Rather than starting from a pre-cleaned Kaggle dataset, this project begins with a 
live API pull of raw, unstructured job posting data (nested JSON, nulls, truncated 
descriptions, mixed currencies) and builds a complete pipeline from there — 
extraction, regex-based skill parsing, a normalized SQLite schema, SQL analysis, 
Python EDA (including a caught-and-corrected currency methodology error), and a 
two-page interactive Power BI dashboard built on custom DAX measures.

Throughout the project, particular emphasis was placed on **not trusting a number 
until its sample size was checked** — a habit that surfaced several real, 
counterintuitive findings, most of them tracing back to structural differences in 
how India's job market data is reported compared to the US and UK.

**Project Scale**
- 450 live job postings collected (150 per country)
- 3 countries: India, United States, United Kingdom
- 17 tracked skills, extracted via regex from titles/descriptions
- 2-page interactive Power BI dashboard with 5 custom DAX measures

## 📑 Table of Contents
- [Project Overview](#-project-overview)
- [Dashboard Preview](#-dashboard-preview)
- [Project Story](#-project-story)
- [Key Findings](#-key-findings)
- [Architecture](#️-architecture)
- [Tech Stack](#️-tech-stack)
- [Repository Structure](#-repository-structure)
- [Notable Problems Solved](#-notable-problems-solved)
- [Data Limitations](#️-data-limitations)
- [About](#-about)

## 📊 Dashboard Preview

This report was built and tested in Power BI Desktop. Due to a Power BI sign-in/
licensing issue encountered during this project, I wasn't able to publish it live 
to the Power BI Service — the screenshots below show both report pages, and the 
full interactive `.pbix` file is included in this repo 
(`dashboard/dashboard.pbix`) and can be opened for free in Power BI Desktop.

**Page 1 — Overview**
*(screenshot: `dashboard/screenshots/01_overview.png`)*

**Page 2 — Skills & Salary Deep Dive**
*(screenshot: `dashboard/screenshots/02_skills_salary.png`)*

## 🧭 Project Story

The dashboard is built around one central question, unpacked across two pages:

> **"What do employers actually want from a Data Analyst — and what does it pay?"**

- **Overview** — Which skills are most in demand, right now, across which markets?
- **Skills & Salary Deep Dive** — Which skills travel together, what do they 
  actually pay once currencies are normalized fairly, and how reliable is any of 
  this given real gaps in the underlying data?

## 🔑 Key Findings

- **SQL is the most in-demand skill overall** (66 mentions), ahead of Power BI (44), 
  Python (35), Excel (33), Tableau (26), and Statistics (22) — and it's also the 
  top skill in both India and the US individually. **Power BI leads instead in the 
  UK** — a genuine cross-country difference, not noise.
- **SQL, Python, Power BI, Excel, and Tableau form a tightly interconnected core 
  skill cluster** (e.g., SQL↔Python co-occur in 30 postings, Power BI↔SQL in 28) — 
  the modern Data Analyst toolkit is a bundle, not a checklist of isolated skills.
- **A naive cross-country salary comparison was actively misleading.** Comparing 
  raw local-currency salaries made India *appear* highest-paying — purely a 
  currency-magnitude artifact (₹1 ≠ $1), not a real pattern. After converting to 
  USD, the corrected picture reverses: **US > UK > India**.
- **~73% of India's job postings are missing salary data entirely**, versus 0% for 
  the US and UK. Initial analysis wrongly implicated the "IT Jobs" category as the 
  cause — a `country + category` breakdown revealed this was a confound: it's a 
  country-level pattern (likely reflecting real regional disclosure norms), not a 
  category effect. India's salary statistics rest on a much smaller effective 
  sample (41 of 150 postings) as a result — surfaced directly on the dashboard, 
  not buried in a footnote.
- **Skill-wise average salary must always be read alongside its posting count.** A 
  skill mentioned in 1–2 postings (e.g., India's Azure) can show an inflated 
  average purely by chance — the dashboard's demand-vs-salary scatter chart makes 
  this distinction visible at a glance rather than letting a misleading number 
  stand alone.

*(Full findings and caveats for every insight are documented inline in this README 
and in the notebooks themselves.)*

## 🏗️ Architecture
Adzuna Jobs API (live, per country)
│
▼
Python — requests + regex-based skill extraction
│
▼
SQLite (db/jobs.db)
├─ jobs table (one row per posting, 450 rows)
└─ job_skills table (one row per job–skill pair, normalized, 275 rows)
│
▼
Python EDA — missingness analysis, currency normalization,
skill co-occurrence, distribution analysis
│
▼
Power BI Desktop
├─ jobs ↔ job_skills relationship (1:many, bidirectional cross-filter)
├─ DAX measures (CALCULATE, MAXX/TOPN, PERCENTILE.INC, context transition)
└─ 2-page interactive report


**Why SQL and Python do the heavy lifting, not Power BI:** cleaning, skill 
extraction, and currency normalization all happen before the data reaches Power 
BI. Power BI's role is deliberately scoped to relational modeling, DAX-driven 
aggregation, and visualization/storytelling — mirroring how this kind of pipeline 
is typically split in practice.

## 🛠️ Tech Stack

- **Data source:** Adzuna Jobs API (live, free-tier)
- **Collection & cleaning:** Python (`requests`, `pandas`, `re`)
- **Database:** SQLite
- **Analysis:** Python (`pandas`, `matplotlib`, `seaborn`), SQL
- **BI/Visualization:** Power BI Desktop (custom DAX, custom JSON theme)
- **SQL concepts demonstrated:** `GROUP BY` + aggregation, `INNER JOIN`, CTEs, 
  window functions (`DENSE_RANK() OVER (PARTITION BY ...)`)
- **DAX concepts demonstrated:** `CALCULATE` and context transition, `SUMMARIZE` + 
  `ADDCOLUMNS`, `TOPN`/`MAXX` for dynamic top-item measures, `PERCENTILE.INC`, 
  relationship cross-filter direction, calculated tables vs. measures

## 📁 Repository Structure
├── README.md
├── scripts/ → pipeline scripts, in run order
│ ├── 01_fetch_jobs.py → Adzuna API extraction
│ ├── 02_clean_data.py → skill extraction, cleaning
│ └── 03_load_to_db.py → SQLite load, schema creation
├── notebooks/
│ ├── 01_sql_queries.ipynb → SQL analysis (joins, CTEs, window fns)
│ └── 02_eda.ipynb → Python EDA, currency normalization,
│ co-occurrence analysis
├── db/
│ └── jobs.db → SQLite database
├── data/processed/
│ └── jobs_clean.csv
└── dashboard/
├── dashboard.pbix → full interactive report file
├── jobs.csv / jobs_skills.csv → Power BI data source
├── skill_gap_theme.json → custom Power BI theme
├── screenshots/ → dashboard page captures
└── images/ → KPI card icons


## 🐛 Notable Problems Solved

- **A misleading cross-country salary chart.** Comparing raw local-currency 
  salaries made India appear highest-paying purely due to currency magnitude. 
  Diagnosed by re-examining the boxplot's axis units, fixed with documented, dated 
  USD conversion rates — and even after conversion, a log scale was still required, 
  since real (not just currency-driven) magnitude differences between countries 
  otherwise collapsed India's data to near-invisibility on a linear axis.
- **A silently confounded root-cause finding.** India's missing-salary rate 
  initially looked like it might be a category effect ("IT Jobs" showing 25% 
  missing). A combined `country + category` breakdown revealed the true driver was 
  country alone — same category, 0% missing in the UK vs. 72% in India.
- **A Power BI relationship silently returning the same value for every group.** A 
  per-skill average salary table showed one identical number for all 17 skills. 
  Traced to the `jobs ↔ job_skills` relationship's cross-filter direction being set 
  to "Single" instead of "Both," verified via a standalone unfiltered baseline 
  comparison before fixing.
- **A DAX context-transition bug.** An aggregate column built inside `ADDCOLUMNS` 
  returned the unfiltered table total for every row until wrapped in `CALCULATE()` 
  — a non-obvious but fundamental DAX rule.
- **A quotes-vs-brackets typo that silently broke a ranking function.** A `TOPN` 
  sort argument referencing `"SkillCount"` (a literal string) instead of 
  `[SkillCount]` (a column reference) caused every row to tie for "top," returning 
  17 rows instead of 1.
- **A KPI card that wouldn't respond to slicer filtering.** Traced to the card 
  pointing at a calculated table (computed once, filter-blind) rather than the 
  equivalent DAX measure (which recalculates per filter context) — a good concrete 
  lesson in when each object type is appropriate.

## ⚠️ Data Limitations

- **Skill detection coverage is ~26%** (117/450 postings had at least one skill 
  detected via regex) — the Adzuna API returns truncated job descriptions, so the 
  true skill mention rate is likely higher than what's captured here.
- **Currency conversion uses a static, dated snapshot rate** (INR→USD, GBP→USD), 
  not live conversion — appropriate for a point-in-time analysis, not for tracking 
  currency-driven salary trends over time.
- **India's postings span a much wider historical date range (2019–2026)** than 
  the US/UK's recent-only postings — likely reflecting differences in how regional 
  job platforms expire/re-index listings, meaning India and US/UK data aren't 
  fully "apples to apples" on recency.
- **India's salary statistics rest on a smaller effective sample** (~27% of its 
  postings) due to its high missing-salary rate — called out explicitly on the 
  dashboard itself.
- **The three countries were sampled at equal size by design** (150 postings each) 
  — the dashboard's country distribution chart reflects collection method, not 
  real-world market share, and is captioned accordingly.

## 📬 About

Built as a portfolio project to demonstrate end-to-end data analyst skills — live 
API data collection, SQL-based analysis, Python EDA and statistical reasoning, and 
Power BI dashboard design with custom DAX — using real, messy, live data rather 
than a pre-cleaned dataset.
