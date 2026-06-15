#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "iPhone (3)";
const char* password = "Kebe1111";

WiFiUDP udp;
unsigned int localPort = 12345;
unsigned int remotePort = 12346;
IPAddress rosIP;
bool ipDetected = false;

float enc_g = 0.0, enc_d = 0.0;
float vitesse = 0.02; // Vitesse de rotation (rad/step)
int cmd = 5;
unsigned long lastMs = 0;
char buffer[255];

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nIP ESP: " + WiFi.localIP().toString());
  udp.begin(localPort);
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    rosIP = udp.remoteIP();
    ipDetected = true;
    int len = udp.read(buffer, 255);
    if (len > 0) buffer[len] = 0;
    cmd = atoi(buffer);
    Serial.printf("CMD: %d\n", cmd);
  }

  if (millis() - lastMs >= 50) {
    // Physique du robot
    if(cmd == 1) { enc_g += vitesse; enc_d += vitesse; }
    else if(cmd == 2) { enc_g -= vitesse; enc_d -= vitesse; }
    else if(cmd == 3) { enc_g -= vitesse; enc_d += vitesse; }
    else if(cmd == 4) { enc_g += vitesse; enc_d -= vitesse; }

    if (ipDetected) {
      udp.beginPacket(rosIP, remotePort);
      udp.print(enc_g); udp.print(","); udp.print(enc_d);
      udp.endPacket();
    }
    lastMs = millis();
  }
}