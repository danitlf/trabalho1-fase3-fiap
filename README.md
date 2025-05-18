# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Nome do projeto
Previsão de Falhas em Equipamentos Industriais com Sensores e IA

## Nome do grupo
Rumo ao NEXT

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

Este repositório contém o código-fonte do sensor inteligente baseado em ESP32 utilizado no projeto acadêmico **FarmTech Solutions**.  
O objetivo é monitorar variáveis agronômicas (pH estimado por LDR, temperatura, umidade relativa, níveis simulados de Fósforo e Potássio) e decidir, em tempo real, quando acionar a bomba de irrigação.  

Os dados coletados são enviados por HTTP POST em formato JSON para um Web Service, permitindo armazenamento em banco de dados e análises posteriores.

## Resumo do Circuito
- **DHT22** — pino 19; use resistor de pull-up de 10 kΩ entre DATA e 3 V3.  
- **LDR** — pino 34 (ADC1_CH6); formar divisor com resistor de 10 kΩ.  
- **Botão “Fósforo”** — pino 23; configurado como `INPUT_PULLUP`.  
- **Botão “Potássio”** — pino 22; configurado como `INPUT_PULLUP`.  
- **Relé da bomba** — pino 12; nível alto liga a bomba.  
- **Alimentação** — ESP32 DevKit v1 alimentado por 5 V USB; GND comum entre todos os componentes.

## Arquitetura do circuito feito no worki.com

<image src="circuito.png" alt="Circuito do projeto" width="100%" height="100%">
  

  > Observação: o pH é simulado a partir da intensidade luminosa do LDR apenas para fins didáticos.  

## Dependências de Software
- **ESP32-Arduino Core** 2.0.x (Wi-Fi, HTTPClient, gerenciamento de tempo)  
- **DHT sensor library** 1.4.x  
- **ArduinoJson** 6.21 ou superior  
- **ctime / time.h** (biblioteca padrão)  

Instale as bibliotecas via Arduino IDE ou configure em `platformio.ini`.

## Lógica de Controle (Fluxo Resumido)
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

## 🔧 Como executar o código
1. Clone o repositório
2. Abra `farmtech_sensor.ino` na Arduino IDE (>= 2.3) ou use PlatformIO.
3. Selecione a placa _ESP32 Dev Module_.
4. Ajuste as credenciais Wi-Fi e o endpoint HTTP no início do arquivo.
5. Compile e grave no ESP32.
6. Abra o Monitor Serial a 115200 baud para observar os logs.

📁 Estrutura de pastas
```
```
├── src/
│ └── farmtech_sensor.ino ← código principal
├── docs/
│ └── circuito_fritzing.png ← diagrama ilustrativo
└── README.md ← este arquivo
```
```
