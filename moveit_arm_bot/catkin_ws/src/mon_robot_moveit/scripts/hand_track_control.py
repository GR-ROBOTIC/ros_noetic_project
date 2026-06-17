#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import rospy
import moveit_commander
import math
import cv2
import mediapipe as mp

def main():
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('telecommande_main_moveit', anonymous=True)
    
    arm = moveit_commander.MoveGroupCommander("arm")
    arm.set_max_velocity_scaling_factor(1.0)
    arm.set_max_acceleration_scaling_factor(1.0)
    
    rospy.loginfo("🤖 Contrôle par MediaPipe actif ! Présentez votre main.")

    # Utilisation des solutions classiques de MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)

    while not rospy.is_shutdown() and cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Tes repères favoris (0: poignet, 4: pouce, 8: index)
                poignet = hand_landmarks.landmark[0]
                index_bout = hand_landmarks.landmark[8]
                pouce_bout = hand_landmarks.landmark[4]

                # Mappage vers ton robot 6 axes
                angle_waist = (poignet.x - 0.5) * -4.0 
                angle_waist = max(min(angle_waist, 1.5), -1.5)

                angle_shoulder = (poignet.y - 0.5) * -2.0
                angle_shoulder = max(min(angle_shoulder, 1.0), -1.0)

                hauteur_relative = poignet.y - index_bout.y
                angle_elbow = (hauteur_relative - 0.3) * 3.0
                angle_elbow = max(min(angle_elbow, 1.5), -1.5)

                distance_pince = math.sqrt((index_bout.x - pouce_bout.x)**2 + (index_bout.y - pouce_bout.y)**2)
                angle_wrist5 = (distance_pince - 0.05) * 5.0
                angle_wrist5 = max(min(angle_wrist5, 1.5), -1.5)

                # Envoi au groupe de planification
                angles_cibles = [angle_waist, angle_shoulder, angle_elbow, 0.0, angle_wrist5, 0.0]

                try:
                    arm.go(angles_cibles, wait=False)
                except Exception:
                    pass

        cv2.imshow('Suivi de main ROS - MediaPipe', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    moveit_commander.roscpp_shutdown()

if __name__ == '__main__':
    main()
