import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as req
import urllib.parse
import csv
import io

# =============== CONFIG GOOGLE AUTH =================
CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = "https://diff-files.streamlit.app/oauth2callback"

AUTH_URL = (
    "https://accounts.google.com/o/oauth2/v2/auth?"
    + urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile"
    })
)

# ================= FUNÇÃO PRINCIPAL =================
def separar_producao(producao_csv, pagamento_csv):

    pagamentos = set()
    reader_pagamentos = csv.DictReader(io.StringIO(pagamento_csv))
    for row in reader_pagamentos:
        pagamentos.add(row["numero_atendimento"].strip())

    producao_reader = csv.DictReader(io.StringIO(producao_csv))
    fieldnames = producao_reader.fieldnames

    paga_output = io.StringIO()
    pendente_output = io.StringIO()

    paga_writer = csv.DictWriter(paga_output, fieldnames=fieldnames)
    pendente_writer = csv.DictWriter(pendente_output, fieldnames=fieldnames)

    paga_writer.writeheader()
    pendente_writer.writeheader()

    for row in producao_reader:
        if row["numero_atendimento"].strip() in pagamentos:
            paga_writer.writerow(row)
        else:
            pendente_writer.writerow(row)

    return paga_output.getvalue(), pendente_output.getvalue()


# =================== INTERFACE =====================
st.title("📊 Separador de Produção x Pagamentos")
st.write("Upload de arquivos CSV com autenticação Google.")

if "user" not in st.session_state:
    st.session_state.user = None

# Se ainda não logado -> mostra botão
if not st.session_state.user:
    st.markdown(f"### 🔐 Para acessar clique abaixo")
    st.markdown(f"[👉 Login com Google]({AUTH_URL})")

# Se redirecionado com código — concluir login
if "code" in st.query_params and not st.session_state.user:
    token_resp = req.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": st.query_params["code"],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }
    ).json()

    id_info = id_token.verify_oauth2_token(
        token_resp["id_token"], requests.Request(), CLIENT_ID
    )
    st.session_state.user = id_info

# ================= CONTEÚDO APÓS LOGIN =================
if st.session_state.user:
    st.success(f"Logado como **{st.session_state.user['email']}**")
    st.image(st.session_state.user["picture"], width=70)
    st.write("---")

    st.subheader("📁 Enviar arquivos")
    producao = st.file_uploader("Producao CSV", type=["csv"])
    pagamento = st.file_uploader("Pagamentos CSV", type=["csv"])

    if producao and pagamento:
        if st.button("Processar 🔄"):
            producao_data = producao.getvalue().decode()
            pagamento_data = pagamento.getvalue().decode()

            paga_csv, pendente_csv = separar_producao(producao_data, pagamento_data)

            st.success("Processamento concluído!")
            st.download_button("⬇ Baixar Produção Paga", paga_csv, "producao_paga.csv")
            st.download_button("⬇ Baixar Produção Pendente", pendente_csv, "producao_pendente.csv")

    st.write("---")
    st.button("Logout", on_click=lambda: st.session_state.clear())
