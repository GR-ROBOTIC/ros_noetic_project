#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import rospy
import moveit_commander
import math
import cv2
import mediapipe as mp

def main():
    # --- Initialisation de ROS et MoveIt ---
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('telecommande_main_moveit', anonymous=True)
    
    arm = moveit_commander.MoveGroupCommander("arm")
    
    # Booster la vitesse pour que le robot suive la main de manière fluide
    arm.set_max_velocity_scaling_factor(1.0)
    arm.set_max_acceleration_scaling_factor(1.0)
    
    rospy.loginfo("🤖 Contrôle par caméra activé ! Placez votre main devant la webcam.")

    # --- Initialisation de MediaPipe Hand Tracking ---
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    # --- Initialisation Webcam ---
    cap = cv2.VideoCapture(0)

    while not rospy.is_shutdown() and cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        # Miroir + conversion couleur pour MediaPipe
        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Dessiner les points de la main sur la vidéo
                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Récupérer les coordonnées du poignet (Point 0) et de la base des doigts
                poignet = hand_landmarks.landmark[0]
                index_base = hand_landmarks.landmark[5]
                index_bout = hand_landmarks.landmark[8]
                pouce_bout = hand_landmarks.landmark[4]

                # --- 1. AXE 1 (Waist) : Suivi horizontal de la main (Coordonnée X) ---
                # On mappe le X de la caméra (0.2 à 0.8) vers les angles du robot (-1.5 à 1.5 rad)
                angle_waist = (poignet.x - 0.5) * -4.0 
                angle_waist = max(min(angle_waist, 1.5), -1.5)

                # --- 2. AXE 2 (Shoulder) : Suivi vertical de la main (Coordonnée Y) ---
                angle_shoulder = (poignet.y - 0.5) * -2.0
                angle_shoulder = max(min(angle_shoulder, 1.0), -1.0)

                # --- 3. AXE 3 (Elbow) : Distance de l'index (Extension du bras) ---
                # Plus l'index monte par rapport au poignet, plus le coude se tend
                hauteur_relative = poignet.y - index_bout.y
                angle_elbow = (hauteur_relative - 0.3) * 3.0
                angle_elbow = max(min(angle_elbow, 1.5), -1.5)

                # --- 4. AXE 5 et 6 : Écartement Pouce / Index (Pince / Poignet) ---
                distance_pince = math.sqrt((index_bout.x - pouce_bout.x)**2 + (index_bout.y - pouce_bout.y)**2)
                # Si la pince est fermée (distance faible), angle faible
                angle_wrist5 = (distance_pince - 0.05) * 5.0
                angle_wrist5 = max(min(angle_wrist5, 1.5), -1.5)

                # Créer le tableau des 6 angles cibles pour le robot (on laisse les autres à 0 pour tester)
                # Ordre : [waist, shoulder, elbow, wrist, joint_5, joint_6]
                angles_cibles = [angle_waist, angle_shoulder, angle_elbow, 0.0, angle_wrist5, 0.0]

                # Envoyer l'ordre de mouvement asynchrone (sans bloquer la vidéo) à MoveIt
                try:
                    arm.go(angles_cibles, wait=False)
                except Exception as e:
                    pass

        # Afficher la fenêtre de la webcam
        cv2.imshow('Telecommande par Vision - Appuyez sur Q pour quitter', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    moveit_commander.roscpp_shutdown()

if __name__ == '__main__':
    main()
