#include <WiFi.h>
#include <WiFiUdp.h>


const char* ssid = "iPhone (3)"; // Nom de votre réseau Wi-Fi
const char* password = "Kebe1111"; 

// IP et port du PC qui fait tourner Python
const char* host = "172.20.10.3";  // mettre l'IP de ton PC
const uint16_t port = 5005;

// ---------- PINS des potentiomètres ----------
const int potPins[6] = {34, 35, 32, 33, 25, 26}; // 6 analog inputs

WiFiClient client;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Connexion Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connexion Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connecté!");
  Serial.print("IP ESP32: "); Serial.println(WiFi.localIP());
}

void loop() {
  // Reconnecter si nécessaire
  if (!client.connected()) {
    Serial.println("Connexion au serveur...");
    if (!client.connect(host, port)) {
      Serial.println("Échec connexion, retry...");
      delay(2000);
      return;
    }
    Serial.println("Connecté au serveur !");
  }

  // Lire les 6 potentiomètres
  float values[6];
  for (int i = 0; i < 6; i++) {
    int raw = analogRead(potPins[i]);        // 0-4095
    values[i] = map(raw, 0, 4095, -1000, 1000) / 1000.0; // Normalisé -1.0 → 1.0
  }

  // Pour le slider 4 (rotation Z), map à -180° → 180°
  values[3] = map(analogRead(potPins[3]), 0, 4095, -180, 180);

  // Construire la chaîne CSV
  String dataStr = "";
  for (int i = 0; i < 6; i++) {
    dataStr += String(values[i], 3); // 3 décimales
    if (i < 5) dataStr += ",";
  }

  // Envoyer au PC
  client.println(dataStr);
  Serial.println("Envoyé: " + dataStr);

  delay(50); // 20 Hz
}
