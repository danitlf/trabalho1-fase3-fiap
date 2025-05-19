# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Nome do projeto
Previsão de Falhas em Equipamentos Industriais com Sensores e IA

## Nome do grupo
Rumo ao NEXT!

## 👨‍🎓 Integrantes: 

- Felipe Livino dos Santos (RM 563187)
- Daniel Veiga Rodrigues de Faria (RM 561410)
- Tomas Haru Sakugawa Becker (RM 564147)
- Daniel Tavares de Lima Freitas (RM 562625)
- Gabriel Konno Carrozza (RM 564468)

## 👩‍🏫 Professores:

### Tutor(a)

- Leonardo Ruiz Orabona

### Coordenador(a)

- ANDRÉ GODOI CHIOVATO

## 📜 Descrição

Este repositório contém o código-fonte do sensor inteligente baseado em ESP32 utilizado no projeto acadêmico FarmTech Solutions.
O objetivo é monitorar variáveis agronômicas — como pH estimado por LDR, temperatura, umidade relativa, além de níveis simulados de fósforo e potássio — e decidir, em tempo real, quando acionar a bomba de irrigação para otimizar o uso de água.

Os dados coletados pelo sensor são enviados via HTTP POST em formato JSON para um Web Service, que permite o armazenamento em banco de dados e análises posteriores.

Para suportar esse fluxo, uma API desenvolvida em Flask recebe e armazena as leituras dos sensores, disponibilizando-as para consulta. Um módulo simula a geração periódica de dados sintéticos, replicando as medições reais, enviando-os automaticamente para a API.

As leituras coletadas são persistidas em um banco de dados SQLite, que registra o sensor, tipo de variável, valor e timestamp da coleta.

Além disso, uma interface interativa em Streamlit apresenta gráficos temporais das variáveis monitoradas — pH, temperatura, umidade, fósforo e potássio —, com filtros por intervalo de datas para análise detalhada.

Esse sistema integrado oferece uma solução completa para aquisição, armazenamento e monitoramento em tempo real de dados agronômicos, facilitando a tomada de decisões inteligentes na irrigação.

## Resumo do Circuito
- **DHT22** — pino 19; use resistor de pull-up de 10 kΩ entre DATA e 3 V3.  
- **LDR** — pino 34 (ADC1_CH6); formar divisor com resistor de 10 kΩ.  
- **Botão “Fósforo”** — pino 23; configurado como `INPUT_PULLUP`.  
- **Botão “Potássio”** — pino 22; configurado como `INPUT_PULLUP`.  
- **Relé da bomba** — pino 12; nível alto liga a bomba.  
- **Alimentação** — ESP32 DevKit v1 alimentado por 5 V USB; GND comum entre todos os componentes.

## Arquitetura do circuito feito no worki.com

<image src="assets/circuito.png" alt="Circuito do projeto" width="100%" height="100%">
  

  > Observação: o pH é simulado a partir da intensidade luminosa do LDR apenas para fins didáticos.  

## Dependências de Software
- **ESP32-Arduino Core** 2.0.x (Wi-Fi, HTTPClient, gerenciamento de tempo)  
- **DHT sensor library** 1.4.x  
- **ArduinoJson** 6.21 ou superior  
- **ctime / time.h** (biblioteca padrão)  

Instale as bibliotecas via Arduino IDE ou configure em `platformio.ini`.

## Lógica de Controle
1. **Inicialização**  
   - Configura pinos dos sensores, botões e relé.  
   - Conecta-se à rede Wi-Fi de testes `Wokwi-GUEST`.  
   - Ajusta o RTC interno com data/hora fixa para demonstração.  

2. **Leitura de Botões**  
   - Pressionar o botão de Fósforo ou Potássio gera valor aleatório entre 10 e 100 e envia imediatamente ao Web Service.  

3. **Coleta Periódica** (a cada 5 s)  
   - pH estimado é calculado a partir do LDR (`map(0-4095 → 14-0)`).  
   - Temperatura e umidade são lidas do DHT22.  
   - Valores são enviados e registrados no monitor serial.  

4. **Acionamento da Irrigação**  
   - A bomba é ligada se **todas** as condições forem verdadeiras:  
     - pH > 9  
     - temperatura > 30 °C  
     - umidade < 50 %  
   - Caso contrário, o relé permanece desligado.  

5. **Envio Web**  
   - Forma JSON com campos `sensor`, `item`, `valor`, `timestamp`.  
   - Envia via HTTP POST e exibe código de resposta.
  
## 🔄 Fluxo de Dados

<image src="assets/sistema.png" alt="Fluxo de dados" width="100%" height="100%">

1. **Sensor ESP32**

2. **API REST** (`main.py`)
   - **POST /readings:** armazena nova leitura.
   - **GET /readings:** lista todas as leituras.
   - **PUT /readings/<id>:** atualiza leitura.
   - **DELETE /readings/<id>:** remove leitura.

3. **Simulador** (`simulator/data_sender.py`)
   - A cada segundo, busca sensores na API.
   - Gera valor aleatório conforme tipo (temperatura, umidade, pH etc.).
   - Envia leitura simulada à API.

4. **Armazenamento**
   - `main.py` também grava todas as leituras no SQLite (`teste.db`), tabela `readings(sensor, item, valor, timestamp)`.

5. **Dashboard Interativo** (`dashboard.py`)
Funcionalidades:
- Gráficos temporais personalizáveis
- Alertas para valores críticos (ex: pH < 5.5)
- Exportação de relatórios em CSV
6. Armazenamento: Persistência em SQLite com schema:

sql
```
CREATE TABLE readings (
    id INTEGER PRIMARY KEY,
    sensor TEXT,
    temperatura REAL,
    umidade REAL,
    ph REAL,
    fosforo INTEGER,
    potassio INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
## 🔧 Como executar o código
1. Clone o repositório
- Abra `farmtech_sensor.ino` na Arduino IDE (>= 2.3) ou use PlatformIO.
- Selecione a placa _ESP32 Dev Module_.
- Ajuste as credenciais Wi-Fi e o endpoint HTTP no início do arquivo.
- Compile e grave no ESP32.
- Abra o Monitor Serial a 115200 baud para observar os logs.
- Acesse simulator/ e crie um venv: python3 -m venv venv.
2. API Flask
- Acesse a pasta do simulador/API: 
```
cd simulator
```
- Crie e ative o ambiente virtual:
```
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```
- Instale as dependências:
```
pip install -r requirements.txt
```
- Inicie a API:
```
flask run --host=0.0.0.0  # API estará em http://localhost:5000
```
4. Simulador de Dados
- Com a API rodando, execute em outro terminal:
```
python data_sender.py
```
5. Dashboard Streamlit
- Volte à pasta raiz e ative o ambiente virtual:
```
cd ..
source simulator/venv/bin/activate  # Usa o mesmo venv da API
```
- Instale o Streamlit:
```
pip install streamlit pandas plotly
```
- Inicie o dashboard:
```
streamlit run dashboard.py
```
- Acesse http://localhost:8501 no navegador.
6. Ingestão de Dados em SQLite 
- Execute para popular o banco de dados:
```
python main.py
```
- Consulta a API e salva leituras em teste.db.

## 📁 Estrutura de pastas
```
FarmTech-Solutions/
├── assets/                   # Arquivos estáticos (imagens, diagramas, logos)
├── simulator/                # Simulador de dados e API Flask
│   ├── app.py                # API Flask (rotas e lógica do servidor)
│   ├── data_sender.py        # Script para gerar dados sintéticos e enviar à API
│   ├── requirements.txt      # Dependências Python (Flask, SQLAlchemy, etc.)
│   └── venv/                 # Ambiente virtual (gerado localmente)
├── src/                      # Código-fonte do firmware (ESP32)
│   └── farmtech_sensor.ino   # Sketch Arduino para o sensor ESP32
├── main.py                   # Script de ingestão de dados (API → SQLite)
├── dashboard.py              # Dashboard interativo (Streamlit)
├── teste.db                  # Banco de dados SQLite (gerado automaticamente)
└── README.md                 # Documentação principal
```

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
