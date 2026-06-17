#!/home/didi/anaconda3/bin/python3
# -*- coding: utf-8 -*-
import sys
import rospy
import math
import cv2
import mediapipe as mp
from sensor_msgs.msg import JointState
from std_msgs.msg import Header

def main():
    # --- Initialisation de ROS ---
    rospy.init_node('telecommande_directe_main', anonymous=True)
    
    # On crée un Publisher qui injecte directement les angles dans RViz en temps réel
    joint_pub = rospy.Publisher('/move_group/fake_controller_joint_states', JointState, queue_size=1)
    # Si le robot ne bouge pas avec le topic ci-dessus, remplace-le par : '/joint_states'
    
    rospy.loginfo("⚡ Contrôle DIRECT actif ! Le robot va suivre vos doigts instantanément sans planification.")

    # --- Initialisation de MediaPipe ---
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    rate = rospy.Rate(30) # Fixe la fréquence à 30 Hz pour une fluidité maximale

    while not rospy.is_shutdown() and cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        # Valeurs par défaut si aucune main n'est détectée
        angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                poignet = hand_landmarks.landmark[0]
                index_bout = hand_landmarks.landmark[8]
                pouce_bout = hand_landmarks.landmark[4]

                # --- Calculs des angles avec tes repères MediaPipe ---
                angle_waist = (poignet.x - 0.5) * -4.0 
                angle_waist = max(min(angle_waist, 3.14), -3.14)

                angle_shoulder = (poignet.y - 0.5) * -2.0
                angle_shoulder = max(min(angle_shoulder, 1.57), -1.57)

                hauteur_relative = poignet.y - index_bout.y
                angle_elbow = (hauteur_relative - 0.3) * 3.0
                angle_elbow = max(min(angle_elbow, 2.09), -2.09)

                distance_pince = math.sqrt((index_bout.x - pouce_bout.x)**2 + (index_bout.y - pouce_bout.y)**2)
                angle_wrist5 = (distance_pince - 0.05) * 5.0
                angle_wrist5 = max(min(angle_wrist5, 3.14), -3.14)

                # Remplissage des angles pour tes 6 axes
                angles = [angle_waist, angle_shoulder, angle_elbow, 0.0, angle_wrist5, 0.0]

        # --- Publication DIRECTE dans ROS ---
        joint_state = JointState()
        joint_state.header = Header()
        joint_state.header.stamp = rospy.Time.now()
        
        # ATTENTION : Remets bien ici les noms exacts de tes joints définis dans ton URDF
        joint_state.name = ['waist_joint', 'shoulder_joint', 'elbow_joint', 'wrist_joint', 'joint_5', 'joint_6']
        joint_state.position = angles

        joint_pub.publish(joint_state)

        cv2.imshow('Controle Direct Live - Sans Planification', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        rate.sleep()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()