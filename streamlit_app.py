import streamlit as st
import pandas as pd
import math

if "refresh" not in st.session_state:
    st.session_state.refresh = 0

if st.button("Atualizar Dados"):
    st.session_state.refresh += 1


@st.cache_data
def get_gdp_data(dummy):
    DATA_FILENAME = "https://raw.githubusercontent.com/m1caelvr/BOT_CEF/refs/heads/main/data/dados.csv"
    raw_gdp_df = pd.read_csv(DATA_FILENAME)
    MIN_YEAR = 1960
    MAX_YEAR = 2022
    gdp_df = raw_gdp_df.melt(
        ["Country Code"],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        "Year",
        "GDP",
    )
    gdp_df["Year"] = pd.to_numeric(gdp_df["Year"])
    return gdp_df


gdp_df = get_gdp_data(st.session_state.refresh)

min_value = gdp_df["Year"].min()
max_value = gdp_df["Year"].max()
from_year, to_year = st.slider(
    "Which years are you interested in?",
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value],
)
countries = gdp_df["Country Code"].unique()
if not len(countries):
    st.warning("Select at least one country")
selected_countries = st.multiselect(
    "Which countries would you like to view?",
    countries,
    ["DEU", "FRA", "GBR", "BRA", "MEX", "JPN"],
)
filtered_gdp_df = gdp_df[
    (gdp_df["Country Code"].isin(selected_countries))
    & (gdp_df["Year"] <= to_year)
    & (from_year <= gdp_df["Year"])
]
st.header("GDP over time", divider="gray")
st.line_chart(
    filtered_gdp_df,
    x="Year",
    y="GDP",
    color="Country Code",
)

first_year = gdp_df[gdp_df["Year"] == from_year]
last_year = gdp_df[gdp_df["Year"] == to_year]

st.header(f"GDP in {to_year}", divider="gray")

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = (
            first_year[first_year["Country Code"] == country]["GDP"].iat[0] / 1000000000
        )
        last_gdp = (
            last_year[last_year["Country Code"] == country]["GDP"].iat[0] / 1000000000
        )

        if math.isnan(first_gdp):
            growth = "n/a"
            delta_color = "off"
        else:
            growth = f"{last_gdp / first_gdp:,.2f}x"
            delta_color = "normal"

        st.metric(
            label=f"{country} GDP",
            value=f"{last_gdp:,.0f}B",
            delta=growth,
            delta_color=delta_color,
        )
