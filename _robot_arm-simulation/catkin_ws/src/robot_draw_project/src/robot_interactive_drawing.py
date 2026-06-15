#!/usr/bin/env python3
import sys
import rospy
import moveit_commander
import geometry_msgs.msg
from interactive_markers.interactive_marker_server import InteractiveMarkerServer
from visualization_msgs.msg import InteractiveMarker, InteractiveMarkerControl, Marker

# Variables globales pour MoveIt
move_group = None
start_pose = None

def callback_craie(feedback):
    """ Cette fonction est appelée AUTOMATIQUEMENT dès que tu bouges la craie dans RViz """
    global move_group, start_pose
    
    # On ne planifie le mouvement que lorsque tu as fini de glisser le marqueur (quand tu lâches le clic)
    if feedback.event_type == feedback.MOUSE_UP:
        rospy.loginfo(f"Nouvelle position de la craie reçue : X={feedback.pose.position.x:.2f}, Y={feedback.pose.position.y:.2f}, Z={feedback.pose.position.z:.2f}")
        
        # Création de la cible pour la buse
        target_pose = geometry_msgs.msg.Pose()
        target_pose.position = feedback.pose.position
        # On garde l'orientation stable du robot pour éviter qu'il se torde
        target_pose.orientation = start_pose.orientation
        
        # Calcul de la trajectoire en ligne droite vers la craie
        (plan, fraction) = move_group.compute_cartesian_path([target_pose], 0.01, True)
        
        if fraction > 0.5:
            rospy.loginfo("Le bras suit la craie...")
            move_group.execute(plan, wait=False) # wait=False pour ne pas bloquer RViz pendant le mouvement
        else:
            rospy.logwarn("Position de craie hors d'atteinte pour le bras !")

def creer_craie_virtuelle(server, position_initiale):
    """ Crée le marqueur interactif (la bille de craie) dans RViz """
    int_marker = InteractiveMarker()
    int_marker.header.frame_id = "base_link" # Lié à la base de ton robot
    int_marker.name = "craie_3d"
    int_marker.description = "Glisse la craie pour faire suivre le robot"
    int_marker.pose.position = position_initiale
    int_marker.scale = 0.15 # Taille des flèches de contrôle

    # 1. Création du visuel de la craie (une petite sphère verte)
    visual_marker = Marker()
    visual_marker.type = Marker.SPHERE
    visual_marker.scale.x = 0.03
    visual_marker.scale.y = 0.03
    visual_marker.scale.z = 0.03
    visual_marker.color.r = 0.0
    visual_marker.color.g = 1.0 # Verte
    visual_marker.color.b = 0.0
    visual_marker.color.a = 1.0

    # Contrôle visuel non-interactif
    visual_control = InteractiveMarkerControl()
    visual_control.always_visible = True
    visual_control.markers.append(visual_marker)
    int_marker.controls.append(visual_control)

    # 2. Ajout des flèches pour bouger sur l'axe X (Rouge)
    control_x = InteractiveMarkerControl()
    control_x.name = "move_x"
    control_x.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
    control_x.orientation.w = 1
    control_x.orientation.x = 1
    int_marker.controls.append(control_x)

    # 3. Ajout des flèches pour bouger sur l'axe Y (Vert)
    control_y = InteractiveMarkerControl()
    control_y.name = "move_y"
    control_y.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
    control_y.orientation.w = 1
    control_y.orientation.z = 1
    int_marker.controls.append(control_y)

    # 4. Ajout des flèches pour bouger sur l'axe Z (Bleu)
    control_z = InteractiveMarkerControl()
    control_z.name = "move_z"
    control_z.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
    control_z.orientation.w = 1
    control_z.orientation.y = 1
    int_marker.controls.append(control_z)

    # Envoyer le marqueur au serveur RViz
    server.insert(int_marker, callback_craie)
    server.applyChanges()

def main():
    global move_group, start_pose
    
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('robot_interactive_drawing_node')
    
    group_name = "bras_impression"
    move_group = moveit_commander.MoveGroupCommander(group_name)
    rospy.sleep(2)
    
    # Obtenir la position actuelle du robot pour y placer la craie au départ
    rospy.loginfo("Initialisation de la craie interactive...")
    start_pose = move_group.get_current_pose().pose
    
    # Position initiale de la craie (un peu en avant de la buse pour commencer)
    position_depart_craie = start_pose.position
    position_depart_craie.x = 0.35
    position_depart_craie.z = 1.0  # Zone de confort détectée précédemment
    
    # Lancement du serveur de marqueurs
    server = InteractiveMarkerServer("dessin_interactif")
    creer_craie_virtuelle(server, position_depart_craie)
    
    rospy.loginfo("Craie prête ! Bouge les flèches dans RViz pour dessiner.")
    rospy.spin() # Laisse le script tourner en permanence

if __name__ == '__main__':
    main()
