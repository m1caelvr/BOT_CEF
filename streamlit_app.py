import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

if "refresh" not in st.session_state:
    st.session_state.refresh = 0
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.today().date()

@st.cache_data
def get_service_data(refresh):
    DATA_FILENAME = "data/dados.csv"
    df = pd.read_csv(DATA_FILENAME, parse_dates=["FECHAMENTO"])
    return df

df = get_service_data(st.session_state.refresh)

with st.sidebar:
    st.header("Menu de Opções")
    if st.button("Atualizar Dados", type="primary", icon=":material/restart_alt:", use_container_width=True):
        st.session_state.refresh += 1

selected_date = st.date_input("Selecionar Data Base:", st.session_state.selected_date)
st.session_state.selected_date = selected_date

date_options = {
    "Hoje": selected_date,
    "Últimos 7 dias": selected_date - timedelta(days=7),
    "Últimos 30 dias": selected_date - timedelta(days=30),
    "Últimos 12 meses": selected_date - timedelta(days=365),
}

date_filter = st.selectbox("Filtrar por período:", list(date_options.keys()), index=2)
filtered_df = df[df["FECHAMENTO"].dt.date >= date_options[date_filter]].copy()

if date_filter == "Hoje":
    filtered_df["Periodo"] = selected_date
    grouped = filtered_df.groupby(["RESPONSÁVEL", "Periodo"]).size().reset_index(name="Ordens de Serviço")
elif date_filter in ["Últimos 7 dias", "Últimos 30 dias", "Últimos 12 meses"]:
    grouped = filtered_df.groupby("RESPONSÁVEL").size().reset_index(name="Ordens de Serviço")

all_technicians = df["RESPONSÁVEL"].unique()
grouped = grouped.set_index("RESPONSÁVEL").reindex(all_technicians, fill_value=0).reset_index()

grouped_for_graph = grouped[grouped["Ordens de Serviço"] > 0]

fig = px.bar(
    grouped_for_graph,
    x="RESPONSÁVEL",
    y="Ordens de Serviço",
    text="Ordens de Serviço",
    title="Ordens de Serviço por Técnico",
    labels={"RESPONSÁVEL": "Técnico", "Ordens de Serviço": "Quantidade"},
)
fig.update_traces(textposition="outside")
fig.update_layout(height=550)

st.header("Ordens de Serviço por Técnico", divider="gray")
st.plotly_chart(fig)

st.header("Resumo das Ordens de Serviço", divider="gray")

grouped = grouped.sort_values(by="Ordens de Serviço", ascending=False)

if date_filter == "Hoje":
    current_start = selected_date
    current_end = selected_date
    previous_start = selected_date - timedelta(days=1)
    previous_end = selected_date - timedelta(days=1)
elif date_filter == "Últimos 7 dias":
    current_start = selected_date - timedelta(days=7)
    current_end = selected_date
    previous_start = selected_date - timedelta(days=14)
    previous_end = selected_date - timedelta(days=7)
elif date_filter == "Últimos 30 dias":
    current_start = selected_date - timedelta(days=30)
    current_end = selected_date
    previous_start = selected_date - timedelta(days=60)
    previous_end = selected_date - timedelta(days=30)
elif date_filter == "Últimos 12 meses":
    current_start = selected_date - timedelta(days=365)
    current_end = selected_date
    previous_start = selected_date - timedelta(days=730)
    previous_end = selected_date - timedelta(days=365)

cols = st.columns(4)

for i, row in grouped.iterrows():
    col = cols[i % len(cols)]
    
    previous_df = df[
        (df["FECHAMENTO"].dt.date >= previous_start) &
        (df["FECHAMENTO"].dt.date <= previous_end)
    ]
    previous_grouped = previous_df.groupby("RESPONSÁVEL").size().reset_index(name="Ordens de Serviço")
    previous_value = previous_grouped.loc[
        previous_grouped["RESPONSÁVEL"] == row["RESPONSÁVEL"],
        "Ordens de Serviço"
    ].sum()

    if previous_value > 0:
        growth_value = row["Ordens de Serviço"] - previous_value
        growth = f"{growth_value:+d}"
    else:
        growth_value = 0
        growth = "0"
    
    if growth_value > 0 or growth_value < 0:
        delta_color = "normal"
    else:
        delta_color = "off"

    with col:
        st.metric(
            label=str(row["RESPONSÁVEL"]),
            value=f"{int(row['Ordens de Serviço'])}",
            delta=growth,
            delta_color=delta_color,
        )
