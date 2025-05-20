#include <DHT.h>
#include <ctime>

//módulos Wifi
#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include <uri/UriBraces.h>

//módulos para webservice
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <string>

#define WIFI_SSID "Wokwi-GUEST"
#define WIFI_PASSWORD ""
#define WIFI_CHANNEL 6

//botoes e sensores
#define botaoFosforo 23    // Pino do botão de Fósforo
#define botaoPotassio 22     // Pino do botão de Potássio
#define ldrPino 34              // Pino analógico do LDR
#define dhtPino 19              // Pino do sensor DHT22
#define relePino 12            // Pino de controle do relé
#define intervaloColeta 5000   // Intervalo de coleta em milissegundos (5 segundos)

// Inicializa o sensor DHT
DHT dht(dhtPino, DHT22);  // Pino e tipo de sensor DHT (DHT22)

unsigned long ultimoTempoColeta = 0; 
int ultimaLeituraLDR = 0; 
float pH = 7.0;
bool releStatus = false;
String motivoAcionamento = "";
int id_coleta = 1;
int valorPotassio = 0;
int valorFosforo = 0;


class ParametrosEnvio{
    public: 
      ParametrosEnvio() : nutriente(nullptr), valor(0.0f) {}
  
      ParametrosEnvio(const char* nutri, float value){ // Usar const char* para literais de string
        nutriente = nutri;
        valor = value;
      }
      const char* getNutriente() const { // Retornar const char* e método const
        return nutriente;
      }
  
      float getValor() const { // Método const
        return valor;
      }
  
    private:
      const char* nutriente; // Armazenar como const char*
      float valor; // Faltava o ponto e vírgula aqui
}; 


//Passar dados para a API postman
HTTPClient http; 

void setup() {
  Serial.begin(115200);
  pinMode(botaoFosforo, INPUT_PULLUP);
  pinMode(botaoPotassio, INPUT_PULLUP);
  pinMode(ldrPino, INPUT);
  pinMode(relePino, OUTPUT); // Configura o pino do relé como saída

  dht.begin();  // Inicializa o sensor DHT

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, WIFI_CHANNEL);
  Serial.print("Conectando ao WiFi ");
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println(" Conectado");

  // Define a data e hora inicial manualmente 
  struct tm timeinfo;
  timeinfo.tm_year = 2025 - 1900; // Ano - 1900
  timeinfo.tm_mon = 05 - 1;       // Mês (0 = Janeiro)
  timeinfo.tm_mday = 10;           // Dia do mês
  timeinfo.tm_hour = 9;           // Hora
  timeinfo.tm_min = 0;            // Minuto
  timeinfo.tm_sec = 0;            // Segundo

  // Configura o RTC do ESP32
  time_t t = mktime(&timeinfo);
  struct timeval now = { .tv_sec = t };
  settimeofday(&now, NULL);  

}

void loop() {
  //leitura dos sensores
  int potassiumButtonState = digitalRead(botaoPotassio);
  int phosphorusButtonState = digitalRead(botaoFosforo);
  
  //leitura potassio
  if (potassiumButtonState == LOW) {
    valorPotassio = random(10, 101);
    delay(1000); 
  }

  //leitura Fosforo
  if (phosphorusButtonState == LOW) {
    valorFosforo = random(10, 101);
    delay(1000);
  }

  // Verifica se já passaram 5 segundos desde a última coleta
  unsigned long tempoAtual = millis();
  if (tempoAtual - ultimoTempoColeta >= intervaloColeta) {
    ultimoTempoColeta = tempoAtual; 

    // Leitura do sensor LDR
    int ldrValue = analogRead(ldrPino);
    float lightIntensity = map(ldrValue, 0, 4095, 14, 0); 

    // Leitura do sensor DHT22 (Temperatura e Umidade)
    float temperatura = dht.readTemperature();
    float umidade = dht.readHumidity();

    // Verifica se houve erro na leitura do DHT22
    if (isnan(temperatura) || isnan(umidade)) {
      Serial.println("Falha na leitura do DHT22!");
      return;
    }

    printData("pH", lightIntensity);
    printData("Temperatura", temperatura);
    printData("Umidade", umidade);
    

    // Verifica as condições para acionar o rele da bomba
    // Se PH maior que 9 e Temperatura > 30°C e umidade < 50%
    // Caso os valores acima estejam válidos é ligada o relé da bomba
    motivoAcionamento = ""; 
    if (lightIntensity > 9 && temperatura > 30 && umidade < 50) {
      releStatus = true;
      motivoAcionamento = "pH > 9, Temperatura > 30°C e Umidade < 50%";
      // Aciona o relé
      digitalWrite(relePino, HIGH); 
      Serial.println("Relé acionado: pH > 10, Temperatura > 30°C e Umidade < 50%");
    } else {
      releStatus = false;
      motivoAcionamento = ""; 
      // Desliga o relé
      digitalWrite(relePino, LOW); 
      Serial.println("Relé desligado");
    }

    const int TIPO_LEITURAS_PROGRAMADAS = 5;
    ParametrosEnvio leiturasProgramadas[TIPO_LEITURAS_PROGRAMADAS];

    leiturasProgramadas[0] = ParametrosEnvio("pH", lightIntensity);
    leiturasProgramadas[1] = ParametrosEnvio("temperatura", temperatura);
    leiturasProgramadas[2] = ParametrosEnvio("umidade", umidade);
    leiturasProgramadas[3] = ParametrosEnvio("potássio", valorPotassio);
    leiturasProgramadas[4] = ParametrosEnvio("fósforo", valorFosforo);

    callWs(leiturasProgramadas, TIPO_LEITURAS_PROGRAMADAS);
  }
}

void printData(char* nutriente, float valor) {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Falha ao obter a data e hora");
    return;
  }

  Serial.printf("%-10d%-20s%-20.2f%-4d-%02d-%02d %02d:%02d:%02d  %-4d%-20s\n",
                id_coleta++,
                nutriente,
                valor,
                timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, timeinfo.tm_mday,
                timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec,
                releStatus, motivoAcionamento.isEmpty() ? "" : motivoAcionamento.c_str());
}

void callWs(ParametrosEnvio leituras[], int numLeituras){
  //link do webservice
  http.begin("https://newsfacd.herokuapp.com/journeybuilder/success"); 
  http.addHeader("Content-Type", "application/json");
  
  //formar arquivo json
  StaticJsonDocument<1024> doc;
  doc["sensor"] = "ESP32";

  struct tm timeinfo;
  if (getLocalTime(&timeinfo)) { // Supondo que getLocalTime() esteja definida e funcionando
    char timestamp[64];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
    doc["timestamp"] = timestamp;
  } else {
    doc["timestamp"] = "N/A"; // Ou algum valor padrão se o tempo não estiver disponível
  }

  JsonArray arrayLeituras = doc.createNestedArray("leituras");

  for (int i = 0; i < numLeituras; ++i) {
    JsonObject leituraObj = arrayLeituras.createNestedObject();
    leituraObj["item"] = leituras[i].getNutriente();
    leituraObj["valor"] = leituras[i].getValor();
  }

  String httpRequestData;
  serializeJson(doc, httpRequestData);

  Serial.println("Enviando JSON para o WebService:");
  Serial.println(httpRequestData);

  int httpResponseCode = http.POST(httpRequestData);
  if (httpResponseCode > 0) {
    Serial.printf("Código de Resposta HTTP: %d\n", httpResponseCode);
    String payload = http.getString();
    Serial.println("Resposta: " + payload);
  } else {
    Serial.printf("Falha na requisição HTTP, erro: %s\n", http.errorToString(httpResponseCode).c_str());
  }
}



