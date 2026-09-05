# Data Analyst Skill Gap Index

Analyzing live job postings across India, US, and UK to answer: 
**"What do employers actually want from a Data Analyst — and what does it pay?"**

## Tech Stack
- **Python** — data collection (API), cleaning, skill extraction (regex-based), EDA
- **SQL (SQLite)** — normalized relational schema, analytical queries
- **Power BI** — interactive two-page dashboard with custom DAX measures

## Data Source
Live job postings pulled from the **Adzuna Jobs API** (developer.adzuna.com), 
covering India (`in`), United States (`us`), and United Kingdom (`gb`), searched 
with the query "data analyst". 450 postings collected (150 per country, 3 pages × 
50 results/page per country — an equal sample size by collection design, not a 
reflection of real-world market share).

## Pipeline Overview
1. **Extraction** (`scripts/fetch_jobs.py`) — pulls job postings via Adzuna API, 
   saves raw JSON per country/page to `data/raw/`
2. **Cleaning + Skill Extraction** (`scripts/clean_data.py`) — flattens nested JSON 
   into a tabular structure, extracts mentioned skills (SQL, Python, Power BI, etc.) 
   from job titles/descriptions via regex pattern matching, saves to 
   `data/processed/jobs_clean.csv`
3. **Database Load** (`scripts/load_to_db.py`) — loads cleaned data into a normalized 
   SQLite database (`db/jobs.db`) with two tables:
   - `jobs` — one row per job posting (450 rows)
   - `job_skills` — one row per (job, skill) pair, normalized for easy skill-level 
     querying (275 rows)
4. **SQL Analysis** (`notebooks/01_sql_queries.ipynb`) — analytical queries: skill 
   demand ranking (aggregation/GROUP BY), salary by skill and country (JOINs), 
   top skill per country (CTEs + window functions/DENSE_RANK)
5. **Python EDA** (`notebooks/02_eda.ipynb`) — missingness analysis, distribution 
   analysis, currency normalization, skill co-occurrence analysis
6. **Power BI Dashboard** — two-page interactive report with custom DAX measures, 
   built on data exported from the Python EDA stage

## Key Findings

### Skill Demand
- **SQL is the most in-demand skill overall** (66 mentions across all postings), 
  ahead of Power BI (44), Python (35), Excel (33), Tableau (26), Statistics (22).
- **By country's top skill:** SQL leads in India (38 postings) and United States 
  (21 postings); **Power BI leads in United Kingdom** (11 postings) — a genuine 
  cross-country difference.
- Only **~26% of postings (117/450)** had at least one skill detected via regex — 
  see Data Limitations for why.

### Salary by Skill — Interpretation Caveats
- Skill-wise average salary must always be interpreted **alongside its posting 
  count**, never alone — a skill mentioned in only 1-2 postings produces an 
  "average" that's really just that single posting's salary, not a reliable 
  market signal (e.g., India's Azure: ₹700,000 avg but only 1 posting).
- Skill-wise average salary is **correlational, not causal/attributive**: since most 
  postings require multiple skills simultaneously, one job's full salary contributes 
  to the average of *every* skill it lists (confirmed via SQL JOIN behavior — a 
  job's salary "fans out" to all its listed skills). A high average for a skill may 
  reflect co-occurrence with other high-paying skills, not its individual value.

### Missing Salary Data — Root Cause Analysis
- **~24% of all postings (109/450)** are missing salary data entirely.
- This missingness is **not random and not category-driven** — it's a **country-level 
  pattern, specifically concentrated in India**:
  - India: **72.7% of postings** missing salary
  - United States: **0% missing**
  - United Kingdom: **0% missing**
- Initial category-level analysis appeared to implicate "IT Jobs" (25.2% missing), 
  since IT Jobs is the dominant category across all countries (401/450 postings). 
  A combined `country + category` breakdown revealed this was a **confound**: 
  India's IT postings are 71.6% missing (141 postings), while UK's IT postings are 
  0% missing (127 postings) — same category, opposite outcome, entirely explained 
  by country, not category.
- **Interpretation:** likely reflects real-world hiring norms — Indian job platforms/
  employers appear to disclose salary far less consistently than US/UK ones.
- **Implication:** India-based salary analysis operates on a much smaller effective 
  sample (~27%, 41/150 postings) than its full posting count suggests. This is 
  called out directly on the Power BI dashboard, not just in this document.

### Posting Date Range — A Third India-Specific Pattern
- Investigation while building the dashboard's date-context header revealed that 
  **India's postings span a much wider historical range (2019–2026)**, while **US 
  and UK postings are tightly clustered around recent dates only**.
- This is a third distinct India-specific data characteristic (alongside missing 
  salary and general data standardization), reinforcing that Adzuna's India index 
  behaves structurally differently from its US/UK indices — likely regional 
  differences in how job platforms manage/expire listings, not a pipeline flaw.
- **Implication:** India and US/UK postings are not fully "apples to apples" in 
  recency; India's dataset mixes years of potentially stale listings with current 
  ones, while US/UK reflect a narrow, current snapshot.

### Currency Normalization — A Methodology Correction
- Initial cross-country salary comparisons used raw local-currency values 
  (INR/GBP/USD) directly, which visually made India appear to have the highest 
  salaries — this was **misleading**, purely an artifact of currency magnitude 
  (₹1 ≠ $1), not real pay differences.
- **Fix:** converted all salaries to USD using documented, dated snapshot exchange 
  rates (INR→USD: 0.0105, GBP→USD: 1.3610, as of Aug 20, 2026 mid-market rates). 
  Static rates, explicitly noted as a simplification — not live-converted.
- **Corrected finding:** once normalized, **United States shows the highest typical 
  salary range, United Kingdom is meaningfully lower, and India is the lowest** — 
  the opposite impression from the uncorrected view.
- Even after normalization, real magnitude differences between countries required 
  a **log scale** in the Python boxplot to keep all three countries visible without 
  one collapsing — India's real-dollar spread is genuinely much smaller than US/UK's.

### Skill Co-occurrence
- SQL, Python, Power BI, Excel, and Tableau form a **tightly interconnected core 
  cluster** — each pairs strongly with the others (e.g., SQL↔Python: 30 co-
  occurrences, Power BI↔SQL: 28, Power BI↔Excel: 22) — the modern Data Analyst 
  toolkit isn't isolated skills, it's a bundle.
- Rarer skills (Azure, SAS, Looker, Big Query, Machine Learning) show low 
  co-occurrence counts with everything — but per the sample-size principle applied 
  throughout this project, these counts are too small (often 1-6) to be trusted as 
  real patterns rather than coincidence.

### Skill Demand vs. Salary (the "reliability" lens)
- **SQL, Power BI, and Python** are the most reliably in-demand skills (35-66 
  postings each), with average USD-normalized pay roughly $65K-77K.
- **Excel** is similarly high-demand (33 postings) but shows notably lower average 
  pay (~$52K) than the other three core skills.
- **Tableau and Statistics** show moderate, still-reasonably-reliable demand 
  (22-26 postings), with pay in the low-to-mid $60Ks.
- **ETL** stands out with unusually high average pay (~$100K+) despite modest 
  demand (15 postings) — an interesting signal, but not statistically confirmed 
  given the smaller sample size.
- The remaining skills (AWS, Alteryx, Machine Learning, Looker, Azure, Spark, 
  Big Query, R) each appear in only a handful of postings (roughly 2-6) — their 
  salary figures are not reliable market signals.
- All skill-based findings are limited by the ~26% skill-detection coverage rate 
  due to truncated job descriptions.

## Known Data Limitations
- **Skill detection coverage: ~26%** of postings had at least one skill detected 
  via regex. The remaining ~74% likely have truncated descriptions from the API. 
  Not corrected via scraping (out of scope / respects API terms of service).
- **Salary currency is not live-converted** — a static, dated exchange-rate snapshot 
  is used (see Currency Normalization above).
- **"Data Analyst" search results skew heavily toward "IT Jobs"** (401/450, ~89%) 
  across all three countries — category is not a useful analytical dimension here; 
  country and skill are the meaningful axes.
- **India's salary statistics rest on a smaller effective sample** (~27%) than its 
  raw posting count suggests, due to the 72.7% missing-salary rate.
- **India's postings span a much wider date range (2019-2026)** than US/UK's 
  recent-only postings — see Posting Date Range above.
- **Missing salary values are intentionally preserved (not imputed) throughout 
  Python EDA** — pandas' native NaN-exclusion in aggregations is relied upon, 
  rather than fabricating estimated values. Handling for dashboard display was 
  deferred to and addressed at the Power BI stage (explicit "27% coverage" callout).

## SQL Highlights (`notebooks/01_sql_queries.ipynb`)
- Skill demand ranking via `GROUP BY` + `COUNT`
- Salary by skill and country via `INNER JOIN` + `GROUP BY`
- Top skill per country via **CTE + `DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...)`**

## Power BI Dashboard

### Design Approach
- Dark, neutral-charcoal custom theme (JSON-based) built around the project's 
  Python color palette (`#2A9D8F`, `#E9C46A`, `#856576`, `#264653`) for visual 
  consistency with the EDA charts.
- Data model: `jobs` and `jobs_skills` tables connected via a one-to-many 
  relationship on `job_id` (cross-filter direction set to "Both" to support 
  bidirectional filtering needed for skill-level aggregation).
- Data exported from Python (`jobs.csv`, `jobs_skills.csv`); DAX handles all 
  in-dashboard calculations (deliberate choice, for hands-on DAX practice).

### Page 1 — Overview
- Header with title, subtitle, and data-extraction date
- Country slicer (India / UK / US) — filters all visuals on the page
- KPI cards: Total Job Postings, Top Skill (dynamic DAX measure), Countries Covered, 
  Count of Skills Tracked
- **Most In-Demand Skills** — horizontal bar chart
- **Skill Demand vs. Salary** — scatter chart pairing demand (count) against average 
  pay, solving the "small sample size looks impressive" trap directly in-dashboard
- **Job Listing Distribution by Country** — donut chart, captioned to clarify equal 
  sample size is by design, not organic market share
- **Top 10 Companies by DA Job Listings** — bar chart

### Page 2 — Skills & Salary Deep Dive
- **Skill Co-occurrence Heatmap** — Matrix visual with conditional background-color 
  formatting; diagonal (self-pairs) masked via DAX `IF()` check
- **Salary Ranges Across Markets (USD-Normalized)** — table with Min/Q1/Median/Q3/Max 
  per country, computed via `PERCENTILE.INC()` DAX measures, cross-validated against 
  Python's `.describe()` output (values matched exactly)
- **Average Salary by Country (USD)** — bar chart with data labels (to keep India's 
  real-dollar value readable despite its visually small bar)
- **Salary Data Coverage callout** — explicit "27% / 41 of 150" note on India's 
  effective salary sample size

### Debugging Notes (real issues encountered and resolved)
1. **Relationship cross-filter direction bug** — per-skill average salary initially 
   showed an identical value for every skill; traced to the relationship's cross-
   filter direction being set to "Single" instead of "Both," which prevented 
   filtering `jobs` based on `jobs_skills[skill]`. Verified via a standalone 
   unfiltered Card comparison before applying the fix.
2. **DAX context transition** — a `SkillCount` column computed inside `ADDCOLUMNS` 
   returned the same (unfiltered) total for every row until wrapped in `CALCULATE()`, 
   which performs the row-context-to-filter-context conversion DAX requires.
3. **`SUMMARIZE` reliability trap** — building an aggregate column inline within 
   `SUMMARIZE` produced unreliable results when later sorted by `TOPN`; fixed by 
   separating into `SUMMARIZE` (grouping only) + `ADDCOLUMNS` (aggregation) as two 
   distinct steps.
4. **Quotes vs. brackets in DAX** — a `TOPN` sort argument referencing `"SkillCount"` 
   (a literal string) instead of `[SkillCount]` (a column reference) caused every 
   row to tie for "top," returning all 17 rows instead of 1.
5. **Calculated table vs. measure** — a Card visual initially pointed to a 
   calculated table (`TopSkillTable`), which is computed once at refresh and does 
   **not** respond to slicer filtering. Switching the Card to reference the 
   equivalent DAX **measure** (which recalculates per filter context) restored 
   correct slicer interactivity.

### Access Note
This dashboard was built and is fully functional in Power BI Desktop, including 
interactive slicers, dynamic DAX measures, and cross-filtering across two pages. 
Due to a Power BI sign-in/licensing issue encountered during this project, it was 
not possible to publish the report to Power BI Service for a live shareable link.

To view/interact with the dashboard:
- **Screenshots**: see `dashboard/screenshots/` for full-page captures of both 
  report pages
- **Live file**: the complete `.pbix` file is included at 
  `dashboard/skill_gap_dashboard.pbix` — open in Power BI Desktop (free) to 
  interact with slicers, drill into visuals, and inspect the DAX measures directly

## Progress Log
- [x] Step 1: Project setup, API credentials
- [x] Step 2: Data collection pipeline
- [x] Step 3: Cleaning, skill extraction, SQLite load
- [x] Step 4: SQL analytical queries
- [x] Step 5: Python EDA (missingness, distributions, currency normalization, 
      co-occurrence)
- [x] Step 6: Power BI dashboard (2 pages, custom theme, DAX measures)
- [ ] Step 7: Statistical hypothesis testing (deferred — e.g., does Python 
      requirement significantly affect salary, controlling for country)
- [ ] Step 8: Final packaging (screenshots, GitHub README polish, resume bullets)