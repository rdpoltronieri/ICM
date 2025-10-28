import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# ------------------------
# CONFIGURAÇÃO INICIAL
# ------------------------
st.set_page_config(page_title="Agenda com Período Personalizado", layout="wide")
st.title("🗓️ Agenda Interativa com Seleção de Período e Banco de Dados")

DB_NAME = "agenda_periodo.db"

# ------------------------
# BANCO DE DADOS
# ------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            horario TEXT,
            nome TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_agenda():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM agenda", conn)
    conn.close()
    return df

def reservar(data, horario, nome):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO agenda (data, horario, nome) VALUES (?, ?, ?)", (data, horario, nome))
    conn.commit()
    conn.close()

def remover(data, horario):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agenda WHERE data = ? AND horario = ?", (data, horario))
    conn.commit()
    conn.close()

def limpar_agenda():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agenda")
    conn.commit()
    conn.close()

init_db()

# ------------------------
# GERAR LISTA DE HORÁRIOS
# ------------------------
inicio = datetime.strptime("00:00", "%H:%M")
fim = datetime.strptime("23:45", "%H:%M")
intervalo = timedelta(minutes=15)

horarios = []
hora = inicio
while hora <= fim:
    horarios.append(hora.strftime("%H:%M"))
    hora += intervalo

# ------------------------
# INTERFACE DE SELEÇÃO
# ------------------------
col1, col2 = st.columns(2)
data_inicio = col1.date_input("📅 Data inicial", datetime.today())
data_fim = col2.date_input("📅 Data final", datetime.today() + timedelta(days=6))

if data_fim < data_inicio:
    st.error("⚠️ A data final deve ser posterior à data inicial.")
    st.stop()

# Gera lista de datas no intervalo
lista_datas = [data_inicio + timedelta(days=i) for i in range((data_fim - data_inicio).days + 1)]
datas_formatadas = [d.strftime("%d/%m/%Y") for d in lista_datas]

st.divider()
st.subheader("Selecione a data e o horário desejado:")

col3, col4 = st.columns(2)
data_selecionada = col3.selectbox("📅 Escolha uma data", datas_formatadas)
nome = col4.text_input("✍️ Digite seu nome para reservar:")

st.divider()
st.subheader(f"Horários para {data_selecionada}")

# Carrega reservas
df_agenda = get_agenda()
reservas_do_dia = df_agenda[df_agenda["data"] == data_selecionada]

# Exibe horários
for h in horarios:
    reservado = reservas_do_dia[reservas_do_dia["horario"] == h]
    col1, col2, col3 = st.columns([1, 3, 2])
    col1.write(h)

    if not reservado.empty:
        pessoa = reservado["nome"].values[0]
        col2.write(f"🔒 Reservado por **{pessoa}**")
        if col3.button("❌ Cancelar", key=f"cancel_{data_selecionada}_{h}"):
            remover(data_selecionada, h)
            st.success(f"Reserva das {h} cancelada.")
            st.rerun()
    else:
        if col3.button("✅ Reservar", key=f"reserva_{data_selecionada}_{h}"):
            if nome.strip():
                reservar(data_selecionada, h, nome.strip())
                st.success(f"Horário {h} reservado com sucesso!")
                st.rerun()
            else:
                st.warning("Digite seu nome antes de reservar.")

st.divider()

# ------------------------
# LIMPAR AGENDA
# ------------------------
if st.button("🧹 Limpar TODAS as reservas (administrador)"):
    limpar_agenda()
    st.warning("Todas as reservas foram apagadas!")
    st.rerun()
