#!/usr/bin/env python3
import sys
import rospy
import moveit_commander
import geometry_msgs.msg
from interactive_markers.interactive_marker_server import *
from visualization_msgs.msg import *

class CustomRobotFollower(object):
    def __init__(self):
        super(CustomRobotFollower, self).__init__()
        
        # 1. Initialisation de MoveIt et du Node ROS
        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node('custom_robot_follower_node', anonymous=True)
        
        # 2. Connexion avec le robot 6 axes
        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()
        
        # ATTENTION : "bras_impression" doit correspondre au nom choisi dans MoveIt
        self.move_group = moveit_commander.MoveGroupCommander("bras_impression")
        
        # Paramètres de précision pour l'impression 3D
        self.move_group.set_goal_position_tolerance(0.005) # 5mm de tolérance
        self.move_group.set_goal_orientation_tolerance(0.02)
        self.move_group.set_max_velocity_scaling_factor(0.2) # Vitesse réduite pour l'exercice
        
        # 3. Initialisation du serveur de marqueurs interactifs pour RViz
        self.server = InteractiveMarkerServer("buse_target_marker")
        self.create_interactive_marker()
        
        rospy.loginfo("🦾 Script de suivi activé ! Déplace le cube vert pour guider la buse.")

    def create_interactive_marker(self):
        # Création du marqueur de base lié au repère d'origine du robot
        int_marker = InteractiveMarker()
        int_marker.header.frame_id = "base_link"
        int_marker.name = "cube_impression"
        int_marker.description = "Point cible de la buse"
        
        # Position initiale du cube (légèrement devant et en hauteur pour que le robot l'atteigne)
        int_marker.pose.position.x = 0.3
        int_marker.pose.position.y = 0.0
        int_marker.pose.position.z = 0.6
        int_marker.scale = 0.15

        # Forme visuelle (Le Cube Vert)
        box_marker = Marker()
        box_marker.type = Marker.CUBE
        box_marker.scale.x = 0.04
        box_marker.scale.y = 0.04
        box_marker.scale.z = 0.04
        box_marker.color.r = 0.1
        box_marker.color.g = 0.8
        box_marker.color.b = 0.1
        box_marker.color.a = 1.0

        box_control = InteractiveMarkerControl()
        box_control.always_visible = True
        box_control.markers.append(box_marker)
        int_marker.controls.append(box_control)

        # Flèches de déplacement (Axes X, Y, Z)
        for direction in ['x', 'y', 'z']:
            control = InteractiveMarkerControl()
            control.name = "move_" + direction
            control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
            if direction == 'x':
                control.orientation.w = 1; control.orientation.x = 1
            elif direction == 'y':
                control.orientation.w = 1; control.orientation.z = 1
            elif direction == 'z':
                control.orientation.w = 1; control.orientation.y = 1
            int_marker.controls.append(control)

        self.server.insert(int_marker, self.process_feedback)
        self.server.applyChanges()

    def process_feedback(self, feedback):
        # Dès que le cube bouge dans RViz
        if feedback.event_type == InteractiveMarkerFeedback.POSE_UPDATE:
            target_pose = geometry_msgs.msg.Pose()
            target_pose.position = feedback.pose.position
            
            # Orientation de la buse pointée vers le bas (0, 1, 0, 0 = rotation de 180° autour de Y)
            target_pose.orientation.x = 0.0
            target_pose.orientation.y = 1.0
            target_pose.orientation.z = 0.0
            target_pose.orientation.w = 0.0

            # Définir la cible et calculer la trajectoire
            self.move_group.set_pose_target(target_pose)
            
            # Exécution en tâche de fond (non-bloquant pour rester fluide)
            self.move_group.go(wait=False)

if __name__ == '__main__':
    try:
        follower = CustomRobotFollower()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass