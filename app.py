import streamlit as st
import pandas as pd

st.set_page_config(page_title="Separador de CSV", layout="centered")
st.title("🔄 Separador CSV — Produção x Pagamentos")

st.write("Envie os dois arquivos CSV para gerar os arquivos separados.")

producao_file = st.file_uploader("📄 Upload do arquivo **producao.csv**", type="csv")
pagamento_file = st.file_uploader("💰 Upload do arquivo **pagamentos.csv**", type="csv")

if producao_file and pagamento_file:
    producao = pd.read_csv(producao_file, dtype=str)
    pagamentos = pd.read_csv(pagamento_file, dtype=str)

    pagos = producao[producao["numero_atendimento"].isin(pagamentos["numero_atendimento"])]
    pendentes = producao[~producao["numero_atendimento"].isin(pagamentos["numero_atendimento"])]

    st.success("✔ Arquivos processados com sucesso!")

    st.subheader("Downloads:")

    st.download_button(
        "📥 Baixar Produção Paga",
        pagos.to_csv(index=False).encode("utf-8"),
        file_name="producao_paga.csv"
    )

    st.download_button(
        "📥 Baixar Produção Pendente",
        pendentes.to_csv(index=False).encode("utf-8"),
        file_name="producao_pendente.csv"
    )
