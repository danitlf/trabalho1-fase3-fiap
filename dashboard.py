# dashboard/app.py  -----------------------------------------------------------
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
# import google.generativeai as genai ### NOVO ###

#---------------------------------------------------------------------#
# CONFIGURAÇÕES GERAIS                                                #
#---------------------------------------------------------------------#
API_URL   = "http://127.0.0.1:8000"      # ajuste se a API rodar noutro host
REFRESH_S = 10                           # intervalo de atualização (segundos)

st.set_page_config(page_title="FarmTech – Dashboard",
                   layout="wide",
                   page_icon="🌱")

# --- ### NOVO ### - Configuração da API do Gemini --------------------#
load_dotenv()
# try:
#     api_key = os.getenv("GOOGLE_API_KEY")
#     if not api_key:
#         api_key = st.secrets["GOOGLE_API_KEY"] # Para deploy no Streamlit Cloud
#     genai.configure(api_key=api_key)
# except Exception:
#     st.error("Chave da API do Google (GOOGLE_API_KEY) não encontrada. Verifique seu arquivo .env ou os secrets do Streamlit.")
#     st.stop()
#---------------------------------------------------------------------#
# FUNÇÕES AUXILIARES (c/ caching do Streamlit)                        #
#---------------------------------------------------------------------#
@st.cache_data(ttl=REFRESH_S)
def listar_sensores():
    r = requests.get(f"{API_URL}/sensores/")
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=REFRESH_S)
def listar_leituras(sensor_id, limite=5000):
    r = requests.get(f"{API_URL}/leituras/{sensor_id}")
    r.raise_for_status()
    data = r.json()[-limite:]
    df = pd.DataFrame(data)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

@st.cache_data(ttl=REFRESH_S)
def esta_chovendo():
    r = requests.get(f"{API_URL}/israinning")
    r.raise_for_status()
    return r.json()["is_raining"]

# --- ### NOVO ### - Funções para Predição e Análise Gemini -----------#
@st.cache_data(ttl=REFRESH_S)
def listar_previsoes(limite=5000):
    """Busca o histórico de previsões para um sensor."""
    try:
        # Assumindo que o endpoint de predições segue o padrão /predicts/{sensor_id}
        r = requests.get(f"{API_URL}/predicts")
        r.raise_for_status()
        data: list = r.json()[-limite:]
        df = pd.DataFrame(data, columns=["valor"])
        # if not df.empty:
            # df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except requests.exceptions.RequestException:
        # Retorna DataFrame vazio se o endpoint não existir ou der erro
        return pd.DataFrame()

# @st.cache_data(ttl=3600) # Cache mais longo para a análise, que é cara
# def gerar_analise_com_gemini(prompt):
#     """Envia um prompt para o Gemini e retorna a análise."""
#     try:
#         model = genai.GenerativeModel('gemini-2.5-flash-05-20')
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         return f"Ocorreu um erro ao gerar a análise: {e}"

# --- Funções de CRUD (sem alteração) -----------------------------------#
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
# SIDEBAR – seleção e ações rápidas (sem alteração)                    #
#---------------------------------------------------------------------#
with st.sidebar:
    st.header("⚙️ Configurações")
    st.subheader("Novo sensor")
    nome_sensor = st.text_input("Nome")
    if st.button("Criar"):
        if nome_sensor:
            criar_sensor(nome_sensor)
            st.cache_data.clear()
        else:
            st.error("Forneça um nome!")

    sensores = listar_sensores()
    if not sensores:
        st.info("Nenhum sensor cadastrado.")
        st.stop()

    opcoes = {f'{s["id"]} – {s["nome"]}': s["id"] for s in sensores}
    selecionados = st.multiselect("Sensores exibidos",
                                  list(opcoes.keys()),
                                  default=list(opcoes.keys())[:1])
    st.subheader("Leitura manual")
    sel_id = st.selectbox("Sensor", selecionados, format_func=lambda k: k.split(" – ")[1])
    val = st.number_input("Valor", step=0.1)
    if st.button("Registrar leitura"):
        if selecionados:
            criar_leitura(opcoes[sel_id], val)
            st.cache_data.clear()

    st.subheader("Excluir sensor")
    del_id = st.selectbox("Escolher", list(opcoes.keys()))
    if st.button("Apagar sensor", type="primary"):
        deletar_sensor(opcoes[del_id])
        st.cache_data.clear()

#---------------------------------------------------------------------#
# MAIN PAGE – dashboards                                              #
#---------------------------------------------------------------------#
st.title("🌾 FarmTech – Monitoramento de Sensores")

is_rain = esta_chovendo()
col_r, col_t = st.columns([1, 4])
col_r.metric("☔️ Vai chover agora?", "Sim" if is_rain else "Não", delta="🌧️" if is_rain else "☀️")
col_t.write("A informação vem de `/israinning` (Open-Meteo). Se **Sim**, avalie pausar a irrigação.")

st.divider()

# --- ### ALTERADO ### - Loop principal com gráficos e análises -------#
for nome in selecionados:
    sid = opcoes[nome]
    df_leituras = listar_leituras(sid)
    df_previsoes = listar_previsoes() ### NOVO ###

    st.subheader(f"Sensor: {nome}")

    if df_leituras.empty:
        st.info("Sem leituras registradas para este sensor ainda.")
        continue

    # --- Métricas Principais (Última Leitura e Última Previsão) ---
    col1, col2 = st.columns(2)
    
    # Última medição
    ultimo = df_leituras.iloc[-1]
    col1.metric("Último valor registrado", f"{ultimo.valor:.2f}",
              ultimo.timestamp.strftime("%d/%m %H:%M"))

    # ### NOVO ### - Status da última previsão
    # if df_previsoes:
    ultima_previsao = df_previsoes.iloc[-1]

    if not df_previsoes.empty:
        status_previsao = "Ação Necessária" if ultima_previsao.valor == 1 else "Normal"
        delta_previsao = "⚠️" if ultima_previsao.valor == 1 else "✅"
        col2.metric("Status da Previsão", status_previsao, delta_previsao,
                    help=f"Última previsão indica estado: {status_previsao}")
    else:
        col2.metric("Status da Previsão", "Sem dados", "❓")
        
    # --- Gráfico Histórico de Leituras ---
    st.line_chart(df_leituras.set_index("timestamp")["valor"],
                  height=200, use_container_width=True)

    # --- ### NOVO ### - Histórico de Predições e Análise com IA ---
    with st.expander("Ver detalhes, histórico de previsões e análise com IA ➜", expanded=False):
        
        # Tabela de leituras
        st.markdown("##### Histórico de Leituras")
        st.dataframe(df_leituras.sort_values("timestamp", ascending=False),
                     use_container_width=True, height=200)

        # # Botão para Análise do Gemini
        # st.markdown("---")
        # st.markdown("##### Análise Inteligente com IA")
        
        # # Usar uma chave única para o botão dentro do loop é crucial!
        # if st.button(f"Gerar Análise para o Sensor {nome.split('–')[1].strip()}", key=f"gemini_btn_{sid}"):
        #     # Construindo o prompt com todos os dados relevantes
        #     prompt = f"""
        #     Você é um especialista em agronomia e análise de dados para agricultura de precisão (FarmTech).
        #     Analise os dados a seguir para o sensor '{nome}' e forneça insights e recomendações práticas para um fazendeiro.

        #     **Contexto Atual:**
        #     - Previsão de chuva para agora: {'Sim' if is_rain else 'Não'}

        #     **Dados Históricos do Sensor (umidade, temperatura, etc.):**
        #     ```
        #     {df_leituras.to_string()}
        #     ```

        #     **Histórico de Previsões do Modelo de Machine Learning (onde 1 = Ação Necessária, 0 = Normal):**
        #     ```
        #     {df_previsoes.to_string() if not df_previsoes.empty else "Nenhuma previsão disponível."}
        #     ```

        #     **Sua Tarefa:**
        #     1.  **Interprete a Tendência:** Analise os dados recentes do sensor. Ele está subindo, descendo ou estável? O que isso significa para a cultura?
        #     2.  **Avalie as Previsões:** Com base no histórico de previsões do modelo, ele tem recomendado ações com frequência? Isso condiz com os dados do sensor?
        #     3.  **Recomendação Consolidada:** Juntando os dados do sensor, a previsão do modelo e a previsão de chuva, qual é a sua recomendação principal para as próximas horas? (Ex: "Pausar irrigação", "Monitorar de perto", "Ação de irrigação recomendada", etc.).

        #     Seja claro, objetivo e use um tom que um agricultor entenda facilmente. Formate sua resposta com Markdown.
        #     """
            
            # with st.spinner("🤖 O Gemini está pensando... Por favor, aguarde um momento."):
            #     analise = gerar_analise_com_gemini(prompt)
            #     st.markdown(analise)

    st.divider()

# --------------------------------------------------------------------#
# Rodapé (sem alteração)                                              #
# --------------------------------------------------------------------#
st.caption("Atualiza a cada "
           f"{REFRESH_S} s • Dados via FastAPI + SQLite • Dashboard Streamlit")