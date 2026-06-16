#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import rospy
import moveit_commander
import math

def main():
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('controle_robot_4axes', anonymous=True)
    
    arm = moveit_commander.MoveGroupCommander("arm")
    
    rospy.sleep(2)
    rospy.loginfo("--- Début du script de contrôle ---")
    
    # 1. On récupère la position actuelle exacte du robot (Garanti le bon nombre d'axes)
    angles_actuels = arm.get_current_joint_values()
    rospy.loginfo(f"Nombre d'axes détectés dans 'arm' : {len(angles_actuels)}")
    rospy.loginfo(f"Angles actuels (rad) : {angles_actuels}")
    
    # 2. On crée la cible en modifiant juste le 1er axe (Waist à 45 degrés pour tester)
    angles_bras_cible = list(angles_actuels)
    angles_bras_cible[0] = math.radians(45) 
    
    rospy.loginfo(f"Envoi de la cible sécurisée : {angles_bras_cible}")
    
    # 3. Exécution du mouvement
    try:
        arm.go(angles_bras_cible, wait=True)
        arm.stop() 
        rospy.loginfo("Mouvement réussi ! Le bras a bougé.")
    except Exception as e:
        rospy.logerr(f"Échec du mouvement : {e}")
    
    rospy.loginfo("--- Fin des mouvements ---")
    moveit_commander.roscpp_shutdown()

if __name__ == '__main__':
    main()
