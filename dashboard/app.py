import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

URL_CSV = (
    "https://raw.githubusercontent.com/m1caelvr/BOT_CEF/refs/heads/main/data/dados.csv"
)

st.title("📊 Dashboard de Chamados")

st.sidebar.header("📌 Opções")
opcao = st.sidebar.selectbox(
    "Escolha uma opção:", ["Visão Geral", "Gráficos", "Tabela"]
)


@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv(URL_CSV)
        df["Prazo"] = pd.to_datetime(df["Prazo"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()


df = carregar_dados()

if not df.empty:
    if opcao == "Visão Geral":
        st.write("### 📂 Dados Carregados")
        st.dataframe(df)

    elif opcao == "Gráficos":
        st.write("### 📊 Gráficos")

        if "Prazo" in df.columns and "Valor" in df.columns:
            st.write("#### 📈 Gráfico de Linha (Prazo x Valor)")
            fig, ax = plt.subplots()
            ax.plot(df["Prazo"], df["Valor"], marker="o", linestyle="-", label="Valor")
            ax.set_xlabel("Prazo")
            ax.set_ylabel("Valor")
            ax.legend()
            plt.xticks(rotation=45)
            st.pyplot(fig)

        if "Status" in df.columns:
            st.write("#### 🥧 Gráfico de Pizza (Distribuição de Status)")
            status_counts = df["Status"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(
                status_counts,
                labels=status_counts.index,
                autopct="%1.1f%%",
                startangle=90,
                colors=plt.cm.Paired.colors,
            )
            ax.axis("equal")
            st.pyplot(fig)

    elif opcao == "Tabela":
        st.write("### 📜 Tabela de Dados")
        st.table(df)
