// --- BIBLIOTECAS OTIMIZADAS ---
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

// --- CONFIGURAÇÕES DE REDE ---
#define WIFI_SSID "Wokwi-GUEST"
#define WIFI_PASSWORD ""
#define RECONNECT_INTERVAL_MS 5000 // Tenta reconectar a cada 5 segundos

// --- PINOS E SENSORES ---
#define BOTAO_FOSFORO_PINO 23
#define BOTAO_POTASSIO_PINO 22
#define LDR_PINO 34
#define DHT_PINO 19
#define RELE_PINO 12
#define DHT_TIPO DHT22

// --- INTERVALOS E CONSTANTES ---
#define INTERVALO_COLETA_MS 5000
#define JSON_DOC_SIZE 512
#define LCD_LARGURA 16
#define LCD_ALTURA 2

// --- INICIALIZAÇÃO DOS COMPONENTES ---
LiquidCrystal_I2C lcd(0x27, LCD_LARGURA, LCD_ALTURA);
DHT dht(DHT_PINO, DHT_TIPO);

// --- ESTRUTURA PARA PASSAR DADOS PARA A TAREFA WEB ---
struct SensorDataPayload {
  int16_t ph_x10;
  int16_t temperatura_x10;
  int16_t umidade_x10;
  int16_t potassio;
  int16_t fosforo;
  bool rele_status;
};

// --- VARIÁVEIS GLOBAIS OTIMIZADAS ---
unsigned long ultimoTempoColeta = 0;
int valorPotassio = 0;
int valorFosforo = 0;
bool releStatus = false;
TaskHandle_t tarefaEnvioHandle = NULL;
TimerHandle_t wifiReconnectTimer;

// Protótipos de Funções
void conectarWiFi();
void printToLcd(const char* linha1, const char* linha2);
void tarefaEnvioWebService(void *parametros);
void WiFiEvent(WiFiEvent_t event);


void setup() {
  Serial.begin(115200);

  wifiReconnectTimer = xTimerCreate("wifiTimer", pdMS_TO_TICKS(RECONNECT_INTERVAL_MS), pdFALSE, (void*)0, [](TimerHandle_t xTimer){ conectarWiFi(); });

  pinMode(BOTAO_FOSFORO_PINO, INPUT_PULLUP);
  pinMode(BOTAO_POTASSIO_PINO, INPUT_PULLUP);
  pinMode(LDR_PINO, INPUT);
  pinMode(RELE_PINO, OUTPUT);
  digitalWrite(RELE_PINO, LOW);

  dht.begin();
  lcd.init();
  lcd.backlight();
  
  WiFi.onEvent(WiFiEvent);

  conectarWiFi();

  struct tm timeinfo;
  timeinfo.tm_year = 2025 - 1900; timeinfo.tm_mon = 5 - 1; timeinfo.tm_mday = 10;
  timeinfo.tm_hour = 9; timeinfo.tm_min = 0; timeinfo.tm_sec = 0;
  time_t t = mktime(&timeinfo);
  struct timeval now = { .tv_sec = t };
  settimeofday(&now, NULL);
}

void loop() {
  if (digitalRead(BOTAO_POTASSIO_PINO) == LOW) {
    valorPotassio = random(10, 101);
  }
  if (digitalRead(BOTAO_FOSFORO_PINO) == LOW) {
    valorFosforo = random(10, 101);
  }

  if (millis() - ultimoTempoColeta >= INTERVALO_COLETA_MS) {
    ultimoTempoColeta = millis();

    uint8_t valorPhInt = map(analogRead(LDR_PINO), 0, 4095, 140, 0);
    int16_t tempInt = (int16_t)(dht.readTemperature() * 10);
    int16_t umidInt = (int16_t)(dht.readHumidity() * 10);

    if (isnan(tempInt / 10.0) || isnan(umidInt / 10.0)) {
      Serial.println("Falha na leitura do sensor DHT!");
      printToLcd("Erro no Sensor", "DHT22 Falhou");
      return;
    }

    const char* motivoAcionamento = "";
    if (valorPhInt > 90 && tempInt > 300 && umidInt < 500) {
      if (!releStatus) {
        releStatus = true;
        digitalWrite(RELE_PINO, HIGH);
        motivoAcionamento = "Niveis criticos";
        Serial.println("Rele LIGADO. Motivo: Niveis criticos.");
        printToLcd("Rele LIGADO", motivoAcionamento);
      }
    } else {
      if (releStatus) {
        releStatus = false;
        digitalWrite(RELE_PINO, LOW);
        motivoAcionamento = "";
        Serial.println("Rele DESLIGADO.");
        printToLcd("Rele DESLIGADO", "");
      }
    }
    
    char linha1[LCD_LARGURA + 1];
    char linha2[LCD_LARGURA + 1];
    snprintf(linha1, sizeof(linha1), "PH:%.1f T:%.1f", valorPhInt/10.0, tempInt/10.0);
    snprintf(linha2, sizeof(linha2), "U:%.1f K:%d P:%d", umidInt/10.0, valorPotassio, valorFosforo);
    if(!releStatus) printToLcd(linha1, linha2);

    SensorDataPayload* payload = new SensorDataPayload{
      (int16_t)valorPhInt, tempInt, umidInt, (int16_t)valorPotassio, (int16_t)valorFosforo, releStatus
    };
    
    if (tarefaEnvioHandle == NULL || eTaskGetState(tarefaEnvioHandle) == eDeleted) {
        xTaskCreate(tarefaEnvioWebService, "WebServiceTask", 8192, (void*)payload, 1, &tarefaEnvioHandle);
    } else {
        Serial.println("A tarefa de envio anterior ainda esta em execucao. Ignorando novo envio.");
        delete payload;
    }
  }
}

void conectarWiFi() {
    Serial.println("Iniciando tentativa de conexao WiFi...");
    printToLcd("Conectando...", WIFI_SSID);
    
    WiFi.disconnect(true); 
    delay(100);
    
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void WiFiEvent(WiFiEvent_t event) {
    Serial.printf("[WiFi Event] evento: %d\n", event);

    switch(event) {
        case ARDUINO_EVENT_WIFI_STA_GOT_IP:
            Serial.println("WiFi conectado!");
            Serial.print("IP: ");
            Serial.println(WiFi.localIP());
            printToLcd("Conectado!", WiFi.localIP().toString().c_str());
            
            if (xTimerIsTimerActive(wifiReconnectTimer)) {
                xTimerStop(wifiReconnectTimer, 0);
            }
            break;

        case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
            Serial.println("WiFi desconectado. Tentando reconectar...");
            printToLcd("WiFi Perdido", "Reconectando...");
            
            xTimerStart(wifiReconnectTimer, 0);
            break;
            
        default:
            break;
    }
}

void printToLcd(const char* linha1, const char* linha2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(linha1);
  lcd.setCursor(0, 1);
  lcd.print(linha2);
}

void tarefaEnvioWebService(void *parametros) {
  SensorDataPayload* dados = (SensorDataPayload*)parametros;

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin("https://newsfacd.herokuapp.com/journeybuilder/success");
    
    http.setTimeout(15000);
    
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<JSON_DOC_SIZE> doc;
    doc["sensor"] = "ESP32_Otimizado";

    struct tm timeinfo;
    if (getLocalTime(&timeinfo, 1000)) {
        char timestamp[32];
        strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
        doc["timestamp"] = timestamp;
    }

    JsonArray leituras = doc.createNestedArray("leituras");
    
    JsonObject phObj = leituras.createNestedObject();
    phObj["item"] = "pH";
    phObj["valor"] = dados->ph_x10 / 10.0;
    
    JsonObject tempObj = leituras.createNestedObject();
    tempObj["item"] = "temperatura";
    tempObj["valor"] = dados->temperatura_x10 / 10.0;

    JsonObject umidObj = leituras.createNestedObject();
    umidObj["item"] = "umidade";
    umidObj["valor"] = dados->umidade_x10 / 10.0;

    JsonObject potassioObj = leituras.createNestedObject();
    potassioObj["item"] = "potassio";
    potassioObj["valor"] = dados->potassio;

    JsonObject fosforoObj = leituras.createNestedObject();
    fosforoObj["item"] = "fosforo";
    fosforoObj["valor"] = dados->fosforo;

    char httpRequestData[JSON_DOC_SIZE];
    serializeJson(doc, httpRequestData, sizeof(httpRequestData));

    Serial.println("\n[TAREFA WEB] Enviando JSON:");
    Serial.println(httpRequestData);

    int httpResponseCode = http.POST(httpRequestData);

    if (httpResponseCode > 0) {
      Serial.printf("[TAREFA WEB] Resposta HTTP: %d\n", httpResponseCode);
    } else {
      Serial.printf("[TAREFA WEB] Falha na requisicao: %s\n", http.errorToString(httpResponseCode).c_str());
    }
    http.end();
  } else {
    Serial.println("[TAREFA WEB] Sem WiFi. Envio cancelado.");
  }
  
  delete dados;
  vTaskDelete(NULL);
}