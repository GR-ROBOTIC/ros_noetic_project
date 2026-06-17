#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import rospy
import moveit_commander
import math
import socket
from sensor_msgs.msg import JointState

# --- CONFIGURATION ---
ESP32_IP = '172.20.10.2'  
PORT = 80
NOM_JOINT_5 = 'joint_5' 
NOM_JOINT_6 = 'joint_6'  # Ajuste le nom si nécessaire selon ton URDF

def envoyer_vers_esp32(v1, v2, v3, v4, v5, v6):
    """ Envoie les 6 angles au format 'v1,v2,v3,v4,v5,v6\n' à l'ESP32 """
    chaine_data = f"{int(v1)},{int(v2)},{int(v3)},{int(v4)},{int(v5)},{int(v6)}\n"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            s.connect((ESP32_IP, PORT))
            s.sendall(chaine_data.encode())
            rospy.loginfo(f"📡 Envoyé (6 Axes) -> {chaine_data.strip()}")
    except Exception as e:
        rospy.logwarn_throttle(5, f"⚠️ Erreur Wi-Fi ESP32: {e}")

def callback_joints(msg):
    try:
        joint_dict = {name: pos for name, pos in zip(msg.name, msg.position)}
        
        # On s'assure que nos 6 axes sont bien présents
        joints_requis = ['waist_joint', 'shoulder_joint', 'elbow_joint', 'wrist_joint', NOM_JOINT_5, NOM_JOINT_6]
        
        if all(j in joint_dict for j in joints_requis):
            j1 = math.degrees(joint_dict['waist_joint'])
            j2 = math.degrees(joint_dict['shoulder_joint'])
            j3 = math.degrees(joint_dict['elbow_joint'])
            j4 = math.degrees(joint_dict['wrist_joint'])
            j5 = math.degrees(joint_dict[NOM_JOINT_5])
            j6 = math.degrees(joint_dict[NOM_JOINT_6])
            
            envoyer_vers_esp32(j1, j2, j3, j4, j5, j6)
            
    except Exception as e:
        print(f"Erreur callback: {e}")

def main():
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('moveit_rviz_to_esp32_bridge_6axes', anonymous=True)
    
    arm = moveit_commander.MoveGroupCommander("arm")
    
    # --- AJUSTEMENT DE LA VITESSE ICI ---
    # 1.0 = Vitesse et accélération maximales (Met 0.5 si tu veux aller à 50%)
    arm.set_max_velocity_scaling_factor(1.0)
    arm.set_max_acceleration_scaling_factor(1.0)
    # -------------------------------------

    rospy.loginfo("=====================================================")
    rospy.loginfo("  PONT CONFIGURÉ POUR 6 AXES (VITESSE MAX)")
    rospy.loginfo("  Cliquez sur 'Execute' dans RViz pour envoyer !")
    rospy.loginfo("=====================================================")
    
    rospy.Subscriber("/joint_states", JointState, callback_joints)
    rospy.spin()
if __name__ == '__main__':
    main()
