#include <WiFi.h>
#include <WiFiUdp.h>

// ==============================================================================
//                    CONFIGURATION DU RÉSEAU WI-FI
// ==============================================================================
// Remplace par le nom (SSID) et le mot de passe de ta box ou de ton partage de connexion
const char* ssid = "iPhone (3)";
const char* password = "Kebe1111";

// Port UDP d'écoute (doit être identique à celui configuré dans le script Python)
const unsigned int localPort = 4210;

WiFiUDP udp;
char packetBuffer[255]; // Buffer de réception pour stocker le message entrant

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n[ESP32-UDP] Initialisation...");

  // Connexion au réseau Wi-Fi local
  WiFi.begin(ssid, password);
  Serial.print("[Wi-Fi] Connexion en cours vers ");
  Serial.print(ssid);

  // Attente de l'établissement de la liaison Wi-Fi
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Affichage de l'adresse IP obtenue par DHCP
  Serial.println("\n[Wi-Fi] Connexion établie avec succès !");
  Serial.print("[Wi-Fi] Adresse IP locale de l'ESP32 : ");
  Serial.println(WiFi.localIP());
  Serial.println("--> Copie cette adresse IP et saisis-la dans ton script Python !");

  // Démarrage de l'écoute des paquets UDP entrants
  udp.begin(localPort);
  Serial.print("[UDP] Écoute active sur le port : ");
  Serial.println(localPort);
}

void loop() {
  // Vérification si un paquet UDP est disponible
  int packetSize = udp.parsePacket();

  if (packetSize > 0) {
    // Lecture des données brutes reçues
    int len = udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0; // Ajout du terminateur de chaîne null pour la sécurité
    }

    // Déclaration des variables destinées à accueillir les angles décodés
    float j1 = 0.0;
    float j2 = 0.0;
    float j3 = 0.0;
    float j4 = 0.0;
    float g1 = 0.0;
    float g2 = 0.0;

    // Décodage de la trame CSV reçue "j1,j2,j3,j4,g1,g2"
    int parsed = sscanf(packetBuffer, "%f,%f,%f,%f,%f,%f", &j1, &j2, &j3, &j4, &g1, &g2);

    // Vérification de l'intégrité de la trame décodée
    if (parsed == 6) {
      // Affichage clair des articulations sur le moniteur série
      Serial.print("Base(J1): ");
      Serial.print(j1, 4);
      Serial.print(" | Épaule(J2): ");
      Serial.print(j2, 4);
      Serial.print(" | Coude(J3): ");
      Serial.print(j3, 4);
      Serial.print(" | Poignet(J4): ");
      Serial.print(j4, 4);
      Serial.print(" | Pince_D1: ");
      Serial.print(g1, 4);
      Serial.print(" | Pince_D2: ");
      Serial.println(g2, 4);
    } else {
      // Alerte en cas de trame tronquée ou mal formatée
      Serial.print("[Erreur] Format de trame incorrect reçu : ");
      Serial.println(packetBuffer);
    }
  }
}