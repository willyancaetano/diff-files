import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as req
import json
import urllib.parse

# Carregar credenciais dos secrets
CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]

REDIRECT_URI = "https://diff-files.streamlit.app/oauth2callback"

# URL de autorização
AUTH_URL = (
    "https://accounts.google.com/o/oauth2/v2/auth?"
    + urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope":"openid email profile"
    })
)

st.title("Login com Google")

if "user" not in st.session_state:
    st.session_state.user = None

# Se ainda não logado → mostra botão
if not st.session_state.user:
    st.markdown(f"[Entrar com Google]({AUTH_URL})")

# Callback depois do login
if "code" in st.query_params:
    code = st.query_params["code"]
    
    # Troca o CODE pelo TOKEN
    token_resp = req.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
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

# Se logado → mostra informações
if st.session_state.user:
    st.success(f"Logado como {st.session_state.user['email']}")
    st.image(st.session_state.user["picture"], width=80)
    st.write(st.session_state.user)
    st.button("Logout", on_click=lambda: st.session_state.clear())
