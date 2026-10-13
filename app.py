"""
Lab 3 Dashboard - Life Expectancy vs GDP per Capita
Advanced Data Analytics & Visualization (Semester V) - deployed in Lab 4

Data: Our World in Data (life-expectancy-vs-gdp-per-capita), loaded live at runtime,
so no CSV is committed to the repository (*.csv and data/ are in .gitignore).
If the OWID download fails, the app falls back to the Gapminder sample bundled with Plotly.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

print("Lab 4: Git basics - Streamlit dashboard starting")

OWID_URL = (
    "https://ourworldindata.org/grapher/life-expectancy-vs-gdp-per-capita.csv"
    "?v=1&csvType=full&useColumnShortNames=false"
)

st.set_page_config(page_title="Life Expectancy vs GDP", page_icon="🌍", layout="wide")


def _find(cols, *keywords, exclude="annotation"):
    """Return the first column whose name contains every keyword (case-insensitive)."""
    for c in cols:
        name = c.lower()
        if all(k in name for k in keywords) and exclude not in name:
            return c
    return None


@st.cache_data(show_spinner="Loading Our World in Data dataset...")
def load_data():
    try:
        raw = pd.read_csv(OWID_URL, storage_options={"User-Agent": "Mozilla/5.0"})
        cols = raw.columns
        rename = {
            "Entity": "country",
            "Code": "code",
            "Year": "year",
            _find(cols, "life"): "life_exp",
            _find(cols, "gdp"): "gdp_pc",
            _find(cols, "population"): "pop",
            _find(cols, "region") or _find(cols, "continent"): "continent",
        }
        df = raw.rename(columns=rename)[list(rename.values())]
        # keep real countries only (OWID aggregates have no ISO code or start with OWID_)
        df = df[df["code"].notna() & ~df["code"].astype(str).str.startswith("OWID")]
        df["continent"] = df.groupby("country")["continent"].transform(lambda s: s.ffill().bfill())
        df = df.dropna(subset=["life_exp", "gdp_pc", "pop", "continent"])
        df["year"] = df["year"].astype(int)
        source = "Our World in Data"
    except Exception as err:  # network issue or schema change -> bundled fallback
        print(f"OWID load failed ({err}); using Plotly Gapminder sample")
        df = px.data.gapminder().rename(
            columns={"lifeExp": "life_exp", "gdpPercap": "gdp_pc", "iso_alpha": "code"}
        )[["country", "code", "year", "life_exp", "gdp_pc", "pop", "continent"]]
        source = "Gapminder (Plotly sample)"
    return df, source


df, source = load_data()

# ---------------- Header ----------------
st.title("🌍 Life Expectancy vs GDP per Capita")
st.caption(f"Lab 3 dashboard, version-controlled with Git and deployed on Streamlit Cloud · Data: {source}")

# ---------------- Filter panel ----------------
st.sidebar.header("Filters")
years = sorted(df["year"].unique())
counts = df.groupby("year")["country"].nunique()
default_year = int(counts[counts >= 0.8 * counts.max()].index.max())  # latest well-covered year
year = st.sidebar.slider("Year", int(years[0]), int(years[-1]), default_year)
continents = sorted(df["continent"].unique())
chosen = st.sidebar.multiselect("Continent", continents, default=continents)
log_x = st.sidebar.checkbox("Log scale for GDP per capita", value=True)

view = df[(df["year"] == year) & (df["continent"].isin(chosen))]

if view.empty:
    st.warning("No data for this selection. Pick another year or add a continent.")
    st.stop()

# ---------------- KPI cards ----------------
prev = df[(df["year"] == year - 1) & (df["continent"].isin(chosen))]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Countries", f"{view['country'].nunique()}")
avg_le = (view["life_exp"] * view["pop"]).sum() / view["pop"].sum()
avg_le_prev = (prev["life_exp"] * prev["pop"]).sum() / prev["pop"].sum() if not prev.empty else None
k2.metric(
    "Avg life expectancy (pop-weighted)",
    f"{avg_le:.1f} yrs",
    f"{avg_le - avg_le_prev:+.2f} vs {year - 1}" if avg_le_prev else None,
)
k3.metric("Median GDP per capita", f"${view['gdp_pc'].median():,.0f}")
k4.metric("Total population", f"{view['pop'].sum() / 1e9:.2f} bn")

# ---------------- Main chart ----------------
st.subheader(f"GDP per capita vs life expectancy, {year}")
fig = px.scatter(
    view,
    x="gdp_pc",
    y="life_exp",
    size="pop",
    color="continent",
    hover_name="country",
    log_x=log_x,
    size_max=55,
    labels={"gdp_pc": "GDP per capita (int. $)", "life_exp": "Life expectancy (years)", "pop": "Population"},
)
fig.update_layout(height=520, legend_title_text="Continent", margin=dict(t=10))
st.plotly_chart(fig, width="stretch")

pos = view[view["gdp_pc"] > 0]
r = np.log(pos["gdp_pc"]).corr(pos["life_exp"])
st.caption(f"Correlation between log GDP per capita and life expectancy in {year}: r = {r:.2f}")

# ---------------- Drill-down ----------------
st.subheader("Country drill-down")
default_country = "India" if "India" in view["country"].values else view["country"].iloc[0]
country = st.selectbox("Choose a country", sorted(view["country"].unique()),
                       index=sorted(view["country"].unique()).index(default_country))
hist = df[df["country"] == country].sort_values("year")

c1, c2 = st.columns(2)
c1.plotly_chart(
    px.line(hist, x="year", y="life_exp", title=f"{country}: life expectancy over time",
            labels={"life_exp": "Years", "year": "Year"}),
    width="stretch",
)
c2.plotly_chart(
    px.line(hist, x="year", y="gdp_pc", title=f"{country}: GDP per capita over time",
            labels={"gdp_pc": "Int. $", "year": "Year"}),
    width="stretch",
)

with st.expander("Show data for the selected year"):
    st.dataframe(
        view.sort_values("life_exp", ascending=False)[["country", "continent", "life_exp", "gdp_pc", "pop"]],
        width="stretch",
        hide_index=True,
    )

print("Dashboard ready - deployed from GitHub to Streamlit Cloud")
