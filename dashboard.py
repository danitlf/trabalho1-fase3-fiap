# dashboard/app.py  -----------------------------------------------------------
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

#---------------------------------------------------------------------#
# CONFIGURAÇÕES GERAIS                                                #
#---------------------------------------------------------------------#
API_URL   = "http://127.0.0.1:8000"       # ajuste se a API rodar noutro host
REFRESH_S = 5                            # intervalo de atualização (segundos)

st.set_page_config(page_title="FarmTech – Dashboard",
                   layout="wide",
                   page_icon="🌱")

#---------------------------------------------------------------------#
# FUNÇÕES AUXILIARES (c/ caching do Streamlit)                        #
#---------------------------------------------------------------------#
@st.cache_data(ttl=REFRESH_S)
def listar_sensores():
    r = requests.get(f"{API_URL}/sensores/")
    r.raise_for_status()
    return r.json()                       # lista de dicts conforme SensorRead

@st.cache_data(ttl=REFRESH_S)
def listar_leituras(sensor_id, limite=5000):
    r = requests.get(f"{API_URL}/leituras/{sensor_id}")
    r.raise_for_status()
    data = r.json()[-limite:]             # última N
    df = pd.DataFrame(data)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

@st.cache_data(ttl=REFRESH_S)
def esta_chovendo():
    r = requests.get(f"{API_URL}/israinning")
    r.raise_for_status()
    return r.json()["is_raining"]

def criar_sensor(nome):
    r = requests.post(f"{API_URL}/sensores/", json={"nome": nome})
    r.raise_for_status()
    st.success(f'Sensor "{nome}" criado!')

def deletar_sensor(sensor_id):
    r = requests.delete(f"{API_URL}/sensores/{sensor_id}")
    r.raise_for_status()
    st.warning(f"Sensor {sensor_id} deletado!")

def criar_leitura(sensor_id, valor):
    r = requests.post(f"{API_URL}/leituras/",
                      json={"sensor_id": sensor_id, "valor": valor})
    r.raise_for_status()
    st.success(f"Leitura {valor} registrada para sensor {sensor_id}")

#---------------------------------------------------------------------#
# SIDEBAR – seleção e ações rápidas                                   #
#---------------------------------------------------------------------#
with st.sidebar:
    st.header("⚙️ Configurações")

    # --- CRUD Sensor -------------------------------------------------#
    st.subheader("Novo sensor")
    nome_sensor = st.text_input("Nome")
    if st.button("Criar"):
        if nome_sensor:
            criar_sensor(nome_sensor)
            st.cache_data.clear()         # força reload
        else:
            st.error("Forneça um nome!")

    # --- Listar sensores disponíveis --------------------------------#
    sensores = listar_sensores()
    if not sensores:
        st.info("Nenhum sensor cadastrado.")
        st.stop()

    opcoes   = {f'{s["id"]} – {s["nome"]}': s["id"] for s in sensores}
    selecionados = st.multiselect("Sensores exibidos",
                                  list(opcoes.keys()),
                                  default=list(opcoes.keys())[:1])

    # --- CRUD Leitura rápida ----------------------------------------#
    st.subheader("Leitura manual")
    sel_id   = st.selectbox("Sensor", selecionados,
                            format_func=lambda k: k.split(" – ")[1])
    val      = st.number_input("Valor", step=0.1)
    if st.button("Registrar leitura"):
        criar_leitura(opcoes[sel_id], val)
        st.cache_data.clear()

    # --- Excluir sensor ---------------------------------------------#
    st.subheader("Excluir sensor")
    del_id = st.selectbox("Escolher", list(opcoes.keys()))
    if st.button("Apagar sensor", type="primary"):
        deletar_sensor(opcoes[del_id])
        st.cache_data.clear()

#---------------------------------------------------------------------#
# MAIN PAGE – dashboards                                              #
#---------------------------------------------------------------------#
st.title("🌾 FarmTech – Monitoramento de Sensores")

# --------------------------------------------------------------------#
# Bloco “tempo / chuva”                                               #
# --------------------------------------------------------------------#
is_rain = esta_chovendo()
col_r, col_t = st.columns([1, 4])
col_r.metric("☔️ Vai chover agora?", "Sim" if is_rain else "Não",
             delta="🌧️" if is_rain else "☀️")
col_t.write(
    "A informação vem de `/israinning` (Open-Meteo). "
    "Se **Sim**, avalie pausar a irrigação."
)

# --------------------------------------------------------------------#
# Gráficos por sensor                                                 #
# --------------------------------------------------------------------#
for nome in selecionados:
    sid = opcoes[nome]
    df  = listar_leituras(sid)

    st.subheader(f"Sensor {nome}")

    if df.empty:
        st.info("Sem leituras registradas ainda.")
        continue

    # Última medição
    ultimo = df.iloc[-1]
    st.metric("Último valor", f"{ultimo.valor:.2f}",
              ultimo.timestamp.strftime("%d/%m %H:%M"))

    # Gráfico histórico
    st.line_chart(df.set_index("timestamp")["valor"],
                  height=200, use_container_width=True)

    # Tabela detalhada (colapsável)
    with st.expander("Ver tabela ➜", expanded=False):
        st.dataframe(df.sort_values("timestamp", ascending=False),
                     use_container_width=True)

# --------------------------------------------------------------------#
# Rodapé                                                              #
# --------------------------------------------------------------------#
st.caption("Atualiza a cada "
           f"{REFRESH_S} s • Dados via FastAPI + SQLite • Dashboard Streamlit")
