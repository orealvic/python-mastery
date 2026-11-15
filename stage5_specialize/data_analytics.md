# Track: Data & Analytics

**Stack:** Jupyter / VS Code notebooks · pandas · Polars · NumPy · DuckDB · matplotlib / seaborn / Altair · SQL

## Milestone 1: NumPy fundamentals
- **Learn:** ndarrays, dtypes, vectorization, broadcasting, boolean masks, aggregation along axes.
- **Build:** rewrite five loop-based functions from Stages 1–2 (stats, normalization, moving average) using NumPy, and benchmark them with `timeit`.
- **Done when:** every function has no Python loop, matches the loop version's results, and is at least 10× faster on 1M elements.

## Milestone 2: pandas core
- **Learn:** Series and DataFrame, reading CSV and Parquet, `loc`/`iloc`, filtering, `groupby`/`agg`, `merge`, `pivot_table`, handling missing data, datetime indexes.
- **Build:** clean and explore a messy public dataset (for example NYC 311 calls, or a Kaggle "dirty" dataset).
- **Done when:** a notebook goes from raw file to tidy DataFrame, documents each cleaning decision, and answers 5 written questions.

## Milestone 3: SQL + DuckDB
- **Learn:** SELECT, JOINs, GROUP BY/HAVING, window functions, CTEs. DuckDB lets you query Parquet and DataFrames directly.
- **Build:** answer the same 5 questions in SQL using DuckDB.
- **Done when:** the SQL and pandas answers match, and you can explain when you'd choose each.

## Milestone 4: Visualization & storytelling
- **Learn:** choosing the right chart, matplotlib's object API, seaborn for statistical plots, Altair for declarative/interactive charts.
- **Build:** a 6-chart report answering one clear question.
- **Done when:** every chart has a title that states the takeaway (not just "Sales by month"), labeled axes and units, and a sentence of interpretation.

## Milestone 5: Polars & scale
- **Learn:** the Polars lazy API, expressions, query optimization, and when data doesn't fit in memory (streaming, Parquet partitioning).
- **Build:** port Milestone 2 to Polars, then run it on a dataset of 5 GB or more.
- **Done when:** the lazy pipeline runs within your machine's memory and you can explain the optimized query plan (`.explain()`).

## Milestone 6: Pipelines & reproducibility
- **Learn:** turning notebooks into modules, testing data transformations, data validation (pandera), scheduling (cron, Prefect or Dagster).
- **Build:** a scheduled pipeline: fetch data, validate it, transform it, write Parquet, render an HTML report.
- **Done when:** it runs from one command on a fresh clone, transformations have unit tests, and bad input data fails loudly.

## Capstone
An end-to-end analysis of a real public dataset that you publish as a blog post or a Quarto/Streamlit app: a question, method, findings, limitations, and reproducible code.

## Key reading
- *Python for Data Analysis*, 3rd ed. (Wes McKinney), free online
- Polars user guide · DuckDB docs
- *Storytelling with Data* (Knaflic)
