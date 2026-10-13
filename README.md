# Life Expectancy vs GDP per Capita — Streamlit Dashboard

Lab 4 (Git Basics for a Python Project) · Advanced Data Analytics & Visualization, Semester V
BSc Data Sciences & Analytics, Ramaiah University of Applied Sciences

This repository version-controls the Lab 3 Streamlit dashboard and deploys it permanently on Streamlit Community Cloud.

## What the dashboard shows

- **Filter panel:** year slider, continent multiselect, log-scale toggle
- **KPI cards:** number of countries, population-weighted average life expectancy (with change from the previous year), median GDP per capita, total population
- **Main chart:** bubble scatter of GDP per capita against life expectancy, bubble size = population, colour = continent
- **Drill-down:** pick a country to see its life expectancy and GDP per capita over time, plus the underlying table

## Data

[Our World in Data — Life expectancy vs. GDP per capita](https://ourworldindata.org/grapher/life-expectancy-vs-gdp-per-capita), read directly from the OWID URL when the app starts. No CSV is stored in the repo (`data/` and `*.csv` are git-ignored). If the download fails, the app falls back to the Gapminder sample bundled with Plotly.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard |
| `requirements.txt` | Python dependencies installed by Streamlit Cloud |
| `README.md` | This description |
| `.gitignore` | Keeps checkpoints, `__pycache__`, `.env`, `data/` and `*.csv` out of Git |

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Git workflow practised

`git init` → `git add` → `git commit` → `git remote add origin` → `git push` (authenticated with a Personal Access Token), followed by a feature branch and a Pull Request into `main`.
