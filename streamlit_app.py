import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

if "refresh" not in st.session_state:
    st.session_state.refresh = 0
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.today().date()


@st.cache_data
def get_service_data(refresh):
    DATA_FILENAME = "https://raw.githubusercontent.com/m1caelvr/BOT_CEF/b235d5e78e41cee3baf2c080626087983415aa45/data/dados.csv"
    df = pd.read_csv(DATA_FILENAME, parse_dates=["FECHAMENTO"])
    return df


df = get_service_data(st.session_state.refresh)

with st.sidebar:
    st.header("Menu de Opções")

    selected_date = st.date_input(
        "Selecionar Data Base:", st.session_state.selected_date
    )
    st.session_state.selected_date = selected_date

    date_options = {
        "Hoje": selected_date,
        "Últimos 7 dias": selected_date - timedelta(days=7),
        "Últimos meses": selected_date.replace(day=1),
        "Últimos anos": selected_date - timedelta(days=365),
    }

    date_filter = st.selectbox(
        "Filtrar por período:", list(date_options.keys()), index=2
    )
    filtered_df = df[df["FECHAMENTO"].dt.date >= date_options[date_filter]].copy()

    if st.button(
        "Atualizar Dados",
        type="primary",
        icon=":material/restart_alt:",
        use_container_width=True,
    ):
        st.session_state.refresh += 1

if date_filter == "Hoje":
    filtered_df["Periodo"] = selected_date
    grouped = (
        filtered_df.groupby(["RESPONSÁVEL", "Periodo"])
        .size()
        .reset_index(name="Ordens de Serviço")
    )
elif date_filter in ["Últimos 7 dias", "Últimos meses", "Últimos anos"]:
    grouped = (
        filtered_df.groupby("RESPONSÁVEL").size().reset_index(name="Ordens de Serviço")
    )

all_technicians = df["RESPONSÁVEL"].unique()
grouped = (
    grouped.set_index("RESPONSÁVEL")
    .reindex(all_technicians, fill_value=0)
    .reset_index()
)

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

st.header("Quantidade de OSs fechadas por Técnico", divider="gray")
st.plotly_chart(fig)

# Resume

st.header("Resumo das Ordens de Serviço", divider="gray")

if date_filter == "Hoje":
    current_start = selected_date
    current_end = selected_date
    previous_start = selected_date - timedelta(days=1)
    previous_end = selected_date - timedelta(days=1)
elif date_filter == "Últimos 7 dias":
    current_start = selected_date - timedelta(days=6)
    current_end = selected_date
    previous_start = selected_date - timedelta(days=14)
    previous_end = selected_date - timedelta(days=7)
elif date_filter == "Últimos meses":
    current_start = selected_date.replace(day=1)
    current_end = selected_date
    previous_start = selected_date.replace(day=1) - relativedelta(months=1)
    previous_end = selected_date.replace(day=1) - timedelta(days=1)
elif date_filter == "Últimos anos":
    current_start = selected_date - timedelta(days=365)
    current_end = selected_date
    previous_start = selected_date - timedelta(days=730)
    previous_end = selected_date - timedelta(days=365)

grouped = grouped.sort_values(by="Ordens de Serviço", ascending=False)
cols = st.columns(4)

for i, row in grouped.iterrows():
    col = cols[i % len(cols)]

    previous_df = df[
        (df["FECHAMENTO"].dt.date >= previous_start)
        & (df["FECHAMENTO"].dt.date <= previous_end)
    ]
    previous_grouped = (
        previous_df.groupby("RESPONSÁVEL").size().reset_index(name="Ordens de Serviço")
    )
    previous_value = previous_grouped.loc[
        previous_grouped["RESPONSÁVEL"] == row["RESPONSÁVEL"], "Ordens de Serviço"
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

if date_filter == "Hoje":
    table_mode = "dias"
elif date_filter == "Últimos 7 dias":
    table_mode = "semanas"
elif date_filter == "Últimos meses" or date_filter == "Últimos anos":
    table_mode = "meses"


def get_intervals(mode, ref_date):
    intervals = []
    if mode == "dias":
        for i in range(5):
            current_day = ref_date - timedelta(days=i)
            intervals.append(
                {
                    "start": current_day,
                    "end": current_day,
                    "label": current_day.strftime("%d/%m/%Y"),
                }
            )
    elif mode == "semanas":
        for i in range(5):
            start = ref_date - timedelta(days=7 + 7 * i)
            end = ref_date - timedelta(days=7 * i)
            intervals.append(
                {
                    "start": start,
                    "end": end,
                    "label": f"{end.strftime('%d/%m/%Y')} a {start.strftime('%d/%m/%Y')}",
                }
            )
    elif mode == "meses":
        month_names = {
            1: "jan",
            2: "fev",
            3: "mar",
            4: "abr",
            5: "mai",
            6: "jun",
            7: "jul",
            8: "ago",
            9: "set",
            10: "out",
            11: "nov",
            12: "dez",
        }
        for i in range(5):
            current_month = ref_date - relativedelta(months=i)
            start = datetime(current_month.year, current_month.month, 1).date()
            next_month = start + relativedelta(months=1)
            end = next_month - timedelta(days=1)
            label = f"{month_names[start.month]}/{start.year}"
            intervals.append({"start": start, "end": end, "label": label})

    return intervals


intervals = get_intervals(table_mode, selected_date)

all_techs = sorted(df["RESPONSÁVEL"].dropna().astype(str).unique())
table_dict = {"Técnicos": all_techs}

for intervalo in intervals:
    label = intervalo["label"]
    counts = []
    for tech in all_techs:
        cnt = df[
            (df["RESPONSÁVEL"].apply(lambda x: str(x)) == tech)
            & (df["FECHAMENTO"].dt.date >= intervalo["start"])
            & (df["FECHAMENTO"].dt.date <= intervalo["end"])
        ].shape[0]
        counts.append(cnt)
    table_dict[label] = counts

table_df = pd.DataFrame(table_dict)
st.header("Histórico de fechamentos:")
st.dataframe(table_df)
