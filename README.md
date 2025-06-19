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
O objetivo é monitorar variáveis agronômicas, como pH estimado por LDR, temperatura, umidade relativa, além de níveis simulados de fósforo e potássio; e decidir, em tempo real, quando acionar a bomba de irrigação para otimizar o uso de água.

Os dados coletados pelo sensor são enviados via HTTP POST em formato JSON para um Web Service, que permite o armazenamento em banco de dados e análises posteriores.

Para suportar esse fluxo, uma API desenvolvida em FastAPI recebe e armazena as leituras dos sensores, disponibilizando-as para consulta. Um módulo simula a geração periódica de dados sintéticos, replicando as medições reais, enviando-os automaticamente para a API.

As leituras coletadas são persistidas em um banco de dados, que registra o sensor, tipo de variável, valor e timestamp da coleta.

Por fim, Este projeto simula e exibe dados de sensores em tempo real. Ele é composto por uma API desenvolvida com FastAPI, que gerencia sensores e leituras armazenadas em um banco SQLite. Um simulador cria automaticamente os sensores (caso não existam) e envia leituras continuamente. Para a visualização, foi criado um dashboard em Streamlit que exibe os dados em tempo real de forma simples e interativa.

## 🔌 1. Simulador de Circuito – Wokwi (ESP32)

- **Conecta-se ao WiFi** automaticamente (`Wokwi-GUEST`).
- **Envio Web**
  - Forma JSON com campos `sensor`, `item`, `valor`, `timestamp`.
  - Envia via HTTP POST e exibe código de resposta.
- **Configura sensores e atuadores**:
  - **Sensor DHT22** (temperatura e umidade).
  - **LDR** (simula valor de pH com inversão).
  - **Botões** para simular **níveis de potássio** e **fósforo**.
  - **Relé** para simular acionamento de bomba.
- Coleta os dados a cada 5 segundos:
  - Temperatura, umidade, pH (via LDR), fósforo e potássio.
- **Regras de acionamento do relé**:
  - Aciona bomba se:
    - pH > 9
    - Temperatura > 30 °C
    - Umidade < 50%
- **Envia os dados coletados em JSON para uma API externa**.
- Também imprime no terminal serial os dados com timestamp formatado.

- **Exibe os dados no display LCD I2C**.
- Exibe informações do PH, Temperatura, Umidade, Potássio e Fósforo, além de caso o Rele ser ligado exibe menssagem de alerta.

  ## Resumo do Circuito

- **LCD I2C** - pino 21/22; Exibir informações dos sensores.
- **DHT22** — pino 19; use resistor de pull-up de 10 kΩ entre DATA e 3 V3.
- **LDR** — pino 34 (ADC1_CH6); formar divisor com resistor de 10 kΩ.
- **Botão “Fósforo”** — pino 23; configurado como `INPUT_PULLUP`.
- **Botão “Potássio”** — pino 22; configurado como `INPUT_PULLUP`.
- **Relé da bomba** — pino 12; nível alto liga a bomba.
- **Alimentação** — ESP32 DevKit v1 alimentado por 3V e 5V USB;

## Arquitetura do circuito feito no worki.com

<image src="assets/circuito.png" alt="Circuito do projeto" width="100%" height="100%">

## Serial plotter

<image src="assets/serial_plotter.png" alt="Serial Plotter" width="100%" height="100%">

## ✨ Melhorias Implementadas: Comparativo das Versões

### 1. Arquitetura: Síncrona vs. Multitarefa (RTOS)

- **Código Antigo:** Utilizava um modelo de execução síncrono. A função `callWs()` era chamada diretamente no `loop()`. Durante o envio dos dados via HTTP, todo o programa ficava **bloqueado**, aguardando a resposta do servidor. Isso significava que, por vários segundos, o ESP32 não conseguia ler sensores, verificar botões ou atualizar seu estado.

- **Código Novo:** Adota uma arquitetura multitarefa usando o **FreeRTOS** (o sistema operacional de tempo real integrado ao ESP32). A comunicação com o Web Service é delegada a uma tarefa separada (`tarefaEnvioWebService`).

- **🚀 Vantagem:** A aplicação se tornou **não-bloqueante e mais responsiva**. O `loop()` principal continua executando e lendo os sensores em intervalos regulares, enquanto a tarefa de envio de dados roda em paralelo. Se a rede estiver lenta, isso não afetará a capacidade do dispositivo de monitorar o ambiente em tempo real.

### 2. Gerenciamento da Conexão WiFi

- **Código Antigo:** A conexão WiFi era tratada de forma muito simples. O código tentava se conectar uma única vez na função `setup()` dentro de um laço `while`. Se a conexão caísse durante a execução, não havia nenhum mecanismo para tentar reconectar, e a chamada HTTP falharia.

- **Código Novo:** Implementa um sistema de gerenciamento de conexão assíncrono.

  - `WiFi.onEvent(WiFiEvent)`: Usa o sistema de eventos do WiFi para reagir instantaneamente a desconexões.
  - `TimerHandle_t wifiReconnectTimer`: Cria um temporizador que tenta reconectar automaticamente em intervalos definidos (`RECONNECT_INTERVAL_MS`) apenas quando a conexão é perdida, sem travar o código.

- **🌐 Vantagem:** O dispositivo se tornou mais **confiável e resiliente a falhas de rede**, garantindo maior tempo de atividade.

### 3. Interface de Usuário e Feedback

- **Código Antigo:** Todo o feedback era enviado via `Serial.print()`. Para inspecionar o estado do dispositivo.

- **Código Novo:** Adiciona um display **LCD I2C** (`LiquidCrystal_I2C`) para feedback visual.

- **🖥️ Vantagem:** Fornece feedback **visual, instantâneo e local** ao usuário. É possível ver o status da conexão WiFi, o endereço IP, leituras de sensores e o status do relé diretamente no dispositivo, tornando-o mais completo e independente.

---

### 4. Organização e Legibilidade do Código

- **Código Antigo:** Usava variáveis com nomes genéricos (ex: `ldrPino`, `dhtPino`) e misturava a lógica de coleta e envio de dados. A classe `ParametrosEnvio` era verbosa para um simples contêiner de dados.

- **Código Novo:** O código foi reestruturado para ser mais limpo e organizado.

  - **`#define`**: Todas as constantes (pinos, intervalos, configurações) foram centralizadas no topo do arquivo, facilitando a configuração.
  - **Protótipos de Funções**: As funções são declaradas no início, melhorando a estrutura geral.
  - **Nomenclatura**: Utiliza nomes mais claros e padronizados (ex: `BOTAO_FOSFORO_PINO`, `INTERVALO_COLETA_MS`).
  - **Estrutura de Dados**: Substitui a classe `ParametrosEnvio` por uma `struct SensorDataPayload`, que é mais leve e eficiente para agrupar dados.

- **🧹 Vantagem:** O código é **mais fácil de ler e escalar**.

---

### 5. Eficiência e Gerenciamento de Memória

- **Código Antigo:** Usava o tipo `float` para as leituras e a classe `String` para `motivoAcionamento`. O uso excessivo da classe `String` pode levar à fragmentação da memória (heap) em execuções de longa duração.

- **Código Novo:** Emprega técnicas de otimização para performance e estabilidade.

  - **Matemática de Ponto Fixo**: Armazena valores de sensores como inteiros (`int16_t`), multiplicados por 10 (ex: `temperatura_x10`). Cálculos com inteiros são muito mais rápidos que com ponto flutuante (`float`). Os valores são convertidos para `float` apenas no momento de criar o JSON.
  - **Alocação Dinâmica Controlada**: Aloca o payload dinamicamente (`new SensorDataPayload`) e o libera (`delete payload`) ao final da tarefa de envio. A vida útil do dado está contida de forma segura dentro da tarefa, evitando estouro de memória.
  - **JSON Seguro**: Limita o tamanho do buffer para a serialização do JSON (`char httpRequestData[JSON_DOC_SIZE]`), prevenindo estouros de buffer.

- **⚡ Vantagem:** **Maior performance computacional, menor consumo de memória e maior estabilidade** para operação contínua por longos períodos.

## 🚀 2. API – FastAPI

**API REST** (`main.py`)

- **POST /readings:** armazena nova leitura.
- **GET /readings:** lista todas as leituras.
- **PUT /readings/<id>:** atualiza leitura.
- **DELETE /readings/<id>:** remove leitura.

- A API está implementada no arquivo `main.py`, e utiliza os arquivos `models.py` e `schemas.py` (dentro da pasta `src/`) para estruturar os dados e validações.
- Ela gerencia duas entidades principais:
  - **Sensores**: identificados por nome, tipo e local.
  - **Leituras**: registros dos valores capturados pelos sensores.
- Os dados são armazenados localmente em um banco de dados **SQLite**, no arquivo `banco.db`.

## 🧪 3. Simulador – Geração de Dados

- O simulador está no arquivo `simulator/simulator.py`.
- O papel dele é simular sensores reais, gerando dados de forma contínua.
- Quando o simulador é iniciado, **ele verifica se os sensores já existem no banco de dados**:
  - Se **não existirem**, ele os **cria automaticamente** usando uma função dedicada.
- Em seguida, entra em um loop `while True`:

  - Envia leituras simuladas para cada sensor periodicamente.
  - Isso permite alimentar o banco de dados com dados "em tempo real".

  ## 📊 3. Dashboard – Visualização com Streamlit

- O dashboard está no arquivo `dashboard.py`.
- Desenvolvido com **Streamlit**, ele oferece uma interface web interativa para visualização dos dados coletados.
- É possível:
  - Ver os dados dos sensores em tempo real.
  - Aplicar filtros e analisar diferentes métricas.

## 🔄 Fluxo de Dados

<image src="assets/sistema.png" alt="Fluxo de dados" width="100%" height="100%">

## 📁 Estrutura de pastas

```
trabalho1-fase3-fiap/
├── assets/                      # Pasta para imagens e arquivos de mídia
│
├── simulator/
│   └── simulator.py             # Simulador: cria os sensores e gera valores continuos para abastecer o banco de dados
│
├── src/                         # Código da API FastAPI
│   ├── models.py                # API para gerenciar duas entidades principais: sensores e leituras.
│   └── schemas.py               # Esquemas (Pydantic) para validação dos dados
│
├── wokwi/                       # Arquivos do simulador Wokwi (ESP32)
│   ├── diagram.json             # Diagrama do circuito
│   ├── libraries.txt            # Bibliotecas necessárias
│   ├── sketch.ino               # Código da simulação (Arduino)
│   └── wokwi-project.txt        # Configuração do projeto Wokwi
│
├── .gitignore                   # Arquivos e pastas ignorados pelo Git
├── Makefile                     # Comandos utilitários para automatizar tarefas
├── README.md                    # Documentação do projeto
├── banco.db                     # Banco de dados SQLite
├── dashboard.py                 # Dashboard em Streamlit
├── main.py                      # Arquivo principal para rodar a API
└── requirements.txt             # Lista de dependências do projeto

```

## 🔧 Como executar o código

Para executar o código deste projeto, siga os passos abaixo:

Pré-requisitos:

- Python 3.8+ instalado
- Virtualenv

```
  pip install virtualenv
```

1. Clone o repositório

- A pasta `wokwi/` contém os arquivos do circuito virtual que simula um **ESP32** com sensores conectados.
- O circuito pode ser simulado diretamente no site [https://wokwi.com](https://wokwi.com), bastando importar os arquivos presente na pasta `/worki`:

-Certifique-se de que o ESP32 esteja conectado ao WiFi (Wokwi-GUEST)

O sketch irá:

- Coletar dados dos sensores (DHT, LDR, botões)
- Acionar o relé com base em condições
- Enviar os dados via HTTP para o WebService

2. Crie e ative o ambiente virtual

```
virtualenv my-env
source my-env/bin/activate    # No Windows: my-env\Scripts\activate
```

3. Instalar dependências do projeto

```
pip install -r requirements.txt
```

4. Banco de Dados
   O projeto utiliza SQLite.

- Certifique-se de que o arquivo banco.db esteja na raiz do projeto.
- Ele já deve conter as tabelas necessárias para sensores e leituras.

5. Execute os componentes do sistema com os comandos presentes no `Makefile`
   ▶️ API (FastAPI)

```
uvicorn main:app --reload
```

- Isso iniciará a API na URL: http://127.0.0.1:8000/docs

▶️ Simulador de Sensores

```
python simulator/simulator.py
```

▶️ Dashboard (Streamlit)

```
streamlit run dashboard.py
```

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
