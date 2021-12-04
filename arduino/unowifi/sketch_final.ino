#include <ArduinoHttpClient.h>
#include <ArduinoJson.h>
#include <WiFiNINA.h>
#include <MQ135.h>

char ssid[] = "SoteloNetwork";
char password[] = "1turr1aga";

int status = WL_IDLE_STATUS;

char server[] = "https://reto-iot.herokuapp.com";

const int DEVICE_ID = 1;

WiFiClient client;
const int APIN = 0;
MQ135 gasSensor = MQ135(APIN);

void setup() {
  Serial.begin(9600);

  while (status != WL_CONNECTED) {
    Serial.println("Attempting to connect to Network: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, password);
    delay(1000);
  }

  Serial.print("Connected to SSID: ");
  Serial.println(WiFi.SSID());
  IPAddress ip = WiFi.localIP();
  IPAddress gateway = WiFi.gatewayIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

}

void loop() {

  DynamicJsonDocument doc1(1024);

  float sensor1 = gasSensor.getRZero();

  doc1["value"] = sensor1;
  doc1["parameterId"] = 1;
  doc1["deviceId"] = DEVICE_ID;

  String postData1;

  serializeJson(doc1, postData1);

  if (client.connectSSL(server, 443)) {
    client.println("POST /logs HTTP/1.1");
    client.println("Host: https://reto-iot.herokuapp.com");
    client.println("Content-Type: application/json");
    client.print("Content-Length: ");
    client.println(postData1.length());
    client.println();
    client.print(postData1);
  }

  if (client.connected()) {
    client.stop();
  }

  Serial.println(postData1);
  delay(20000);

}
