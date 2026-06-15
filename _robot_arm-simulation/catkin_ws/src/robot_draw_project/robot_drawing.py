#!/usr/bin/env python3
import sys
import math
import rospy
import moveit_commander
import geometry_msgs.msg

def executer_dessin():
    # 1. Initialisation de MoveIt et du nœud ROS
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('robot_drawing_node', anonymous=True)
    
    group_name = "bras_impression"
    move_group = moveit_commander.MoveGroupCommander(group_name)
    
    rospy.sleep(2) 
    
    # 2. Récupérer la position réelle de départ du robot
    rospy.loginfo("Récupération de la position actuelle du robot...")
    try:
        start_pose = move_group.get_current_pose().pose
    except Exception as e:
        rospy.logerr("Impossible de récupérer la pose actuelle : " + str(e))
        return

    # 3. Génération des points basée sur la vraie hauteur de ton robot (Z = 1.25)
    # On se place là où le robot est déjà à l'aise au démarrage
    centre_x = 0.35  # On projette à 35 cm devant la base
    centre_y = 0.0   # Centré
    centre_z = start_pose.position.z - 0.20 # On descend de 20 cm sous sa position haute pour dessiner
        
    waypoints = []
    rospy.loginfo(f"Calcul du dessin centré sur : X={centre_x:.2f}, Y={centre_y:.2f}, Z={centre_z:.2f}")
    
    # Génération d'un cercle de 5 cm de rayon
    for i in range(30):
        angle = i * (2 * math.pi / 30)
        rayon = 0.05 
        
        pose = geometry_msgs.msg.Pose()
        pose.position.x = centre_x + rayon * math.cos(angle)
        pose.position.y = centre_y + rayon * math.sin(angle)
        pose.position.z = centre_z # Dessin à plat
        
        # Copie de l'orientation initiale de ton robot pour éviter les torsions impossibles
        pose.orientation = start_pose.orientation
        
        waypoints.append(pose)

    # 4. CORRECTION DU TYPE : True (bool) au lieu de 0.0 (float) pour éviter le bug Boost.Python
    # Arguments : (liste_points, pas_en_metres, eviter_collisions)
    (plan, fraction) = move_group.compute_cartesian_path(waypoints, 0.01, True)
    
    rospy.loginfo(f"Trajectoire cartésienne calculée à {fraction * 100:.1f}% par MoveIt")
    
    # 5. Exécution du tracé si MoveIt valide le chemin
    if fraction > 0.8: 
        rospy.loginfo("Exécution de la trajectoire fluide en cours...")
        move_group.execute(plan, wait=True)
        rospy.loginfo("Dessin terminé avec succès ! 🚀")
    else:
        rospy.logerr("Le solveur n'arrive pas à créer de ligne droite à cette hauteur. Tente de modifier centre_z ou centre_x.")

if __name__ == '__main__':
    try:
        executer_dessin()
    except rospy.ROSInterruptException:
        pass