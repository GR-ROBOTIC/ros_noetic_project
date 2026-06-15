#include <WiFi.h>
#include <WiFiUdp.h>

// --- CONFIGURATION WIFI ---
const char* ssid = "iPhone (3)";
const char* password = "Kebe1111";

// ===== CONFIGURATION MOTEURS =====
#define M1_IN1 25
#define M1_IN2 26
#define M2_IN1 12
#define M2_IN2 13

// --- CONFIGURATION UDP ---
WiFiUDP udp;
unsigned int localPort = 12345;
unsigned int remotePort = 12346;
IPAddress rosIP;
bool ipDetected = false;

// --- CONFIGURATION ENCODEURS ---
const int PIN_CLK_L = 19; const int PIN_DT_L = 18;
const int PIN_CLK_R = 34; const int PIN_DT_R = 35;

volatile long enc_l = 0; 
volatile long enc_r = 0;
long last_print_l = 0; 
long last_print_r = 0;
int lastClkL, lastClkR;

// --- INTERRUPTIONS (Lecture des encodeurs) ---
void IRAM_ATTR readEncL() {
  int clk = digitalRead(PIN_CLK_L);
  if (clk != lastClkL && clk == LOW) {
    if (digitalRead(PIN_DT_L) != clk) enc_l++; else enc_l--;
  }
  lastClkL = clk;
}

void IRAM_ATTR readEncR() {
  int clk = digitalRead(PIN_CLK_R);
  if (clk != lastClkR && clk == LOW) {
    if (digitalRead(PIN_DT_R) != clk) enc_r++; else enc_r--;
  }
  lastClkR = clk;
}

unsigned long lastMs = 0;
char buffer[255];
int cmd = 5; // 5 = STOP

void setup() {
  Serial.begin(115200);

  // Initialisation Moteurs
  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);
  pinMode(M2_IN1, OUTPUT);
  pinMode(M2_IN2, OUTPUT);
  
  // Arrêt de sécurité au démarrage
  digitalWrite(M1_IN1, LOW); digitalWrite(M1_IN2, LOW);
  digitalWrite(M2_IN1, LOW); digitalWrite(M2_IN2, LOW);

  // Initialisation Encodeurs
  pinMode(PIN_CLK_L, INPUT_PULLUP); pinMode(PIN_DT_L, INPUT_PULLUP);
  pinMode(PIN_CLK_R, INPUT); pinMode(PIN_DT_R, INPUT); 

  lastClkL = digitalRead(PIN_CLK_L);
  lastClkR = digitalRead(PIN_CLK_R);

  attachInterrupt(digitalPinToInterrupt(PIN_CLK_L), readEncL, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_CLK_R), readEncR, CHANGE);

  // Connexion WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nESP Connecté ! IP: " + WiFi.localIP().toString());
  udp.begin(localPort);
}

void loop() {
  // 1. RECEPTION DES COMMANDES UDP
  int packetSize = udp.parsePacket();
  if (packetSize) {
    rosIP = udp.remoteIP();
    ipDetected = true;
    int len = udp.read(buffer, 255);
    if (len > 0) buffer[len] = 0;
    cmd = atoi(buffer);
    Serial.printf(">>> CMD Reçue: %d\n", cmd);
  }

  // 2. LOGIQUE MOTEURS
  switch(cmd) {
    case 1: // AVANCER
      digitalWrite(M1_IN1, LOW);  digitalWrite(M1_IN2, HIGH);
      digitalWrite(M2_IN1, LOW);  digitalWrite(M2_IN2, HIGH);
      break;
    case 2: // RECULER
      digitalWrite(M1_IN1, HIGH); digitalWrite(M1_IN2, LOW);
      digitalWrite(M2_IN1, HIGH); digitalWrite(M2_IN2, LOW);
      break;
    case 3: // GAUCHE
      digitalWrite(M1_IN1, HIGH); digitalWrite(M1_IN2, LOW);
      digitalWrite(M2_IN1, LOW);  digitalWrite(M2_IN2, HIGH);
      break;
    case 4: // DROITE
      digitalWrite(M1_IN1, LOW);  digitalWrite(M1_IN2, HIGH);
      digitalWrite(M2_IN1, HIGH); digitalWrite(M2_IN2, LOW);
      break;
    default: // STOP (case 5 et autres)
      digitalWrite(M1_IN1, LOW);  digitalWrite(M1_IN2, LOW);
      digitalWrite(M2_IN1, LOW);  digitalWrite(M2_IN2, LOW);
      break;
  }

  // 3. ENVOI DES ENCODEURS ET PRINT DEBUG
  if (millis() - lastMs >= 50) {
    
    // Affichage moniteur série si mouvement
    if (enc_l != last_print_l || enc_r != last_print_r) {
      Serial.printf("ENCODEURS | G: %ld | D: %ld\n", enc_l, enc_r);
      last_print_l = enc_l;
      last_print_r = enc_r;
    }

    // Envoi UDP vers ROS
    if (ipDetected) {
      udp.beginPacket(rosIP, remotePort);
      udp.print(enc_l); 
      udp.print(","); 
      udp.print(enc_r);
      udp.endPacket();
    }
    lastMs = millis();
  }
}