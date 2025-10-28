import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DO FIREBASE ---
cred = credentials.Certificate("firebase_config.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://SEU-PROJETO.firebaseio.com/'  # substitua aqui pelo seu link real
    })

# --- CONFIGURAÇÕES DO APP ---
st.set_page_config(page_title="Corrente de Oração", page_icon="🙏", layout="centered")
st.title("🙏 Corrente de Oração - 27/10 a 01/11")
st.markdown("Escolha um horário de 15 em 15 minutos. O horário escolhido valerá para **todos os dias do período**.")

# --- GERAÇÃO AUTOMÁTICA DOS HORÁRIOS ---
def gerar_horarios():
    inicio = datetime.strptime("00:00", "%H:%M")
    horarios = [(inicio + timedelta(minutes=15 * i)).strftime("%H:%M") for i in range(96)]
    return horarios

horarios = gerar_horarios()

# --- CONEXÃO COM O BANCO ---
ref = db.reference("horarios_geral")

# Cria a estrutura inicial se ainda não existir
if not ref.get():
    dados_iniciais = {h: "" for h in horarios}
    ref.set(dados_iniciais)

dados = ref.get()

# --- INTERFACE PRINCIPAL ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📅 Horários disponíveis (válidos para todo o período):")
    for h in horarios:
        nome = dados.get(h, "")
        if nome == "":
            st.markdown(f"🟢 **{h}** — *Disponível*")
        else:
            st.markdown(f"🔴 **{h}** — Escolhido por: **{nome}**")

with col2:
    st.subheader("🙋‍♂️ Reservar seu horário")
    nome = st.text_input("Digite seu nome completo:")
    opcoes_disponiveis = [h for h in horarios if dados.get(h, "") == ""]
    hora_escolhida = st.selectbox("Escolha um horário:", opcoes_disponiveis)

    if st.button("Confirmar horário"):
        if not nome.strip():
            st.warning("Por favor, insira seu nome antes de confirmar.")
        else:
            # Atualiza o horário para todos os dias (na prática, todos compartilham o mesmo registro)
            ref.child(hora_escolhida).set(nome.strip())
            st.success(f"⏰ Horário {hora_escolhida} reservado para {nome} (válido de 27/10 a 01/11).")
            st.rerun()