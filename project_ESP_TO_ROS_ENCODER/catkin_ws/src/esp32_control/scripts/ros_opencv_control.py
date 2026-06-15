#!/usr/bin/env python3
import rospy
import cv2
import socket
import numpy as np

# Configuration UDP (Même IP que pour ton GUI)
ESP32_IP = "172.20.10.2" # <--- Mets l'IP de ton ESP32 ici
ESP32_PORT = 12345

def opencv_control():
    rospy.init_node('opencv_control_node')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Initialisation de la caméra (0 = webcam par défaut)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        rospy.logerr("Impossible d'ouvrir la caméra")
        return

    print("--- CONTRÔLE OPENCV ACTIVÉ ---")
    print("Touches : Z(1), S(2), Q(3), D(4), Espace(5), M(6)")
    print("Appuyez sur 'ESC' pour quitter")

    while not rospy.is_shutdown():
        ret, frame = cap.read()
        if not ret:
            break

        # Ajouter du texte sur l'image pour faire "Interface Pro"
        cv2.putText(frame, "MODE: CONTROLE CLAVIER", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Afficher la fenêtre
        cv2.imshow("Vue Robot - OpenCV", frame)

        # Gestion des touches clavier
        key = cv2.waitKey(1) & 0xFF

        cmd = None
        if key == ord('z'): cmd = "1" # HAUT
        elif key == ord('s'): cmd = "2" # BAS
        elif key == ord('q'): cmd = "3" # GAUCHE
        elif key == ord('d'): cmd = "4" # DROITE
        elif key == ord(' '): cmd = "5" # STOP
        elif key == ord('m'): cmd = "6" # MANUEL
        
        if cmd:
            sock.sendto(cmd.encode(), (ESP32_IP, ESP32_PORT))
            rospy.loginfo(f"Touche pressée -> CMD {cmd} envoyée à l'ESP32")

        # Quitter avec ESC
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        opencv_control()
    except rospy.ROSInterruptException:
        pass