#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

const char* ssid = "Milo";
const char* password = "97274340";
String wallet = "5D2fBKHgezt6pKKuXFo8Xse3sT9hZK5PtkJEyacozZJnVXZ3";
String token = "0ce956fc-131b-42d6-a4b1-8e8319e45f84";
String serverName = "http://ec2-54-234-110-184.compute-1.amazonaws.com:8086/data_co/";
String source = "Sensor_bici";
const int sensorPin = A0;
int sensorValue = 0;
int ledPin = 5;

WiFiClient wifiClient;

void setup() {

  pinMode(ledPin, OUTPUT);
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  delay(500);

  while (WiFi.status() != WL_CONNECTED) {
 
    delay(1000);
    Serial.println("Connecting..");
    
    }

  // Mensaje exito conexión
  Serial.println("======================================");
  Serial.print("Conectado a:\t");
  Serial.println(WiFi.SSID()); 
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());
  Serial.println("======================================"); 
  
}


void loop() {
  

  sensorValue = analogRead(sensorPin) * 10;
  Serial.println(sensorValue);
  
   
  if (WiFi.status() == WL_CONNECTED) { 

  HTTPClient http;  
  String serverPath = serverName + "?co2=" + sensorValue + "&origin=" + source + "&wallet_send=" + wallet + "&token=" + token; 

  http.begin(wifiClient, serverPath);                         
  int httpCode = http.GET();                                 
  Serial.println("request OK");

  digitalWrite(ledPin, HIGH); // turn the ledPin on
  delay(500); // wait for a second
  digitalWrite(ledPin, LOW); // turn the ledPin off
  delay(500); // wait for a second

  if (httpCode > 0) { 

    String payload = http.getString();   
    Serial.println(payload);            

    }
  
  http.end();
  
  }

  digitalWrite(ledPin, HIGH); // turn the ledPin on
  delay(500); // wait for a second
  digitalWrite(ledPin, LOW); // turn the ledPin off
  delay(500); // wait for a second
  
  delay(15000);
    

}
