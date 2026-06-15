#include <WiFi.h>
#include <WiFiUdp.h>


const char* ssid = "iPhone (3)"; // Nom de votre réseau Wi-Fi
const char* password = "Kebe1111"; 


WiFiUDP Udp;
unsigned int localPort = 5005;

char incomingPacket[128];  // Buffer pour recevoir

void setup() {
  Serial.begin(115200);

  // Connexion Wi-Fi
  WiFi.begin(ssid, password);
  Serial.println("Connexion au Wi-Fi...");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connecté !");
  Serial.print("Adresse IP de l'ESP32 : ");
  Serial.println(WiFi.localIP());   // Affiche l'IP ici

  // Démarrage UDP
  Udp.begin(localPort);
  Serial.printf("UDP en écoute sur le port %d\n", localPort);
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int len = Udp.read(incomingPacket, 128);
    if (len > 0) incomingPacket[len] = 0;

    // Parse CSV
    float tf3x, tf3y, tf3z, tf4x, tf4y, tf4z;
    sscanf(incomingPacket, "%f,%f,%f,%f,%f,%f",
           &tf3x, &tf3y, &tf3z,
           &tf4x, &tf4y, &tf4z);

    Serial.print("TF3 -> ");
    Serial.print("x:"); Serial.print(tf3x);
    Serial.print(" y:"); Serial.print(tf3y);
    Serial.print(" z:"); Serial.println(tf3z);

    Serial.print("TF4 -> ");
    Serial.print("x:"); Serial.print(tf4x);
    Serial.print(" y:"); Serial.print(tf4y);
    Serial.print(" z:"); Serial.println(tf4z);
  }
  delay(10);
}