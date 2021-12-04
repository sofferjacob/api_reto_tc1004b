// Sketch para el ESP8266
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <Arduino_JSON.h>

const char* ssid = "Jacobo Soffer's iPhone"; // nombre de red
const char* pass = "a9ff6cjhi5hn";  // contraseña red
const String url = "https://api-reto.herokuapp.com";

String mac = "";
int deviceId = -1;
const int APIN = 0;
HTTPClient http;
WiFiClient client;



void setup() {
  Serial.begin(9600);
  Serial.print("Conectando a: ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Tratando de conectar...");
    delay(500);
  }
  Serial.println("Coneccion establecida!");
  Serial.print("Dirección ip: ");
  Serial.println(WiFi.localIP());
  mac = WiFi.macAddress();
  // Registro dispositivo
  http.begin(client, url + "/devices/m" + mac);
  int code = http.GET();
  if (code == HTTP_CODE_NOT_FOUND) {
    // Registrar dispositivo y reintentar
    http.end();
    DynamicJsonDocument body(1024);
    body["mac"] = mac;
    body["locationId"] = 2;
    body["modeld"] = 1;
    String reqBody;
    serializeJson(body, reqBody);
    http.begin(client, url + "/devices");
    http.addHeader("Content-Type", "application/json");
    int code = http.POST(reqBody);
    if (code != HTTP_CODE_CREATED) {
      Serial.print("Error registrando dispositivo, código: ");
      Serial.println(code);
      while(true) {}
    }
    http.end();
    http.begin(client, url + "/devices/m" + mac);
    int dcode = http.GET();
    if (dcode != HTTP_CODE_OK) {
      Serial.println("Could not get device id");
      while (true) {}
    }
    String strRes = http.getString();
    JSONVar res = JSON.parse(strRes);
    deviceId = res["id"];
  } else {
    String strRes = http.getString();
    JSONVar res = JSON.parse(strRes);
    deviceId = res["id"];
  }
  http.end();
  if (deviceId == -1) {
    Serial.println("Error obteniendo deviceId");
    while (true) {}
  }
}

void loop() {
  DynamicJsonDocument doc1(1024);
  
  float sensor1 = -1;

  while (sensor1 == -1) {
    if (Serial.available()) {
      String input = Serial.readStringUntil('\n');
      sensor1 = input.toFloat();
    }
  }

  doc1["value"] = sensor1;
  doc1["parameterId"] = 1;
  doc1["deviceId"] = deviceId;

  String postData1;

  serializeJson(doc1, postData1);

  Serial.println("[HTTP] /logs");

  http.begin(client, url + "/logs");
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(postData1);
  Serial.printf("[HTTP] ... código %d\n", code);
  delay(5000); 
}
