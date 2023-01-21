/*
  The app is based on this project https://RandomNerdTutorials.com/esp8266-nodemcu-http-get-post-arduino/
  The regular WiFiClient substitued by WiFiClientSecure.
  Used materials for transitioning to https:
  https://github.com/esp8266/Arduino/blob/master/libraries/ESP8266WiFi/examples/HTTPSRequest/HTTPSRequest.ino
  https://maakbaas.com/esp8266-iot-framework/logs/https-requests/
*/

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include "elebot_cfg.h"

#define ELEBOT_PING_PERIOD_S 30
#define ELEBOT_PING_PERIOD_MS ELEBOT_PING_PERIOD_S *1000

const char* ssid = WIFI_SSID;
const char* password = WIFI_PASS;

//Your Domain name with URL path or IP address with path
String serverName = "https://kstaroverov.pythonanywhere.com/ele_bot_ping";

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long lastTime = 0;
// Timer set to ELEBOT_PING_PERIOD_MS ms
unsigned long timerDelay = ELEBOT_PING_PERIOD_MS;

void setup() {
  Serial.begin(9600); 
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
 
  Serial.println("EleBot is set to send a ping message to EleBot server every " + String(ELEBOT_PING_PERIOD_S) + " seconds (counted by timerDelay variable).");
  Serial.println("To change it, modify the ELEBOT_PING_PERIOD_S constant in elebot_cfg.h.");
  
}

void loop() {
  // Send an HTTP POST request depending on timerDelay
  if ((millis() - lastTime) > timerDelay) {
    //Check WiFi connection status
    if(WiFi.status()== WL_CONNECTED){
      WiFiClientSecure client;
      HTTPClient http;
      String macAddr = WiFi.macAddress();
      String serverPath = serverName + "?device_id=" + macAddr + "&ping_period_s=" + String(ELEBOT_PING_PERIOD_S);
      
      // Trust to pythonanythere assumed.
      client.setInsecure();
      // Your Domain name with URL path or IP address with path
      http.begin(client, serverPath.c_str());
  
      // If you need Node-RED/server authentication, insert user and password below
      //http.setAuthorization("REPLACE_WITH_SERVER_USERNAME", "REPLACE_WITH_SERVER_PASSWORD");
        
      // Send HTTP GET request
      int httpResponseCode = http.GET();
      if (httpResponseCode>0) {
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
        String payload = http.getString();
        Serial.println(payload);
      }
      else {
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
      }
      // Free resources
      http.end();
    }
    else {
      Serial.println("WiFi Disconnected");
    }
    lastTime = millis();
  }
}