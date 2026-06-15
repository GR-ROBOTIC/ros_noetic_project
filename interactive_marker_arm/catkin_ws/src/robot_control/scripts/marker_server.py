#!/usr/bin/env python3
import rospy
import math
import threading
import socket
from interactive_markers.interactive_marker_server import InteractiveMarkerServer
from interactive_markers.menu_handler import MenuHandler
from visualization_msgs.msg import InteractiveMarker, InteractiveMarkerControl, Marker
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Quaternion

class RobotIKController:
    def __init__(self):
        rospy.init_node("robot_joint_controller")
        
        # Dimensions physiques du robot (issues de l'URDF)
        self.shoulder_z = 0.325  # Hauteur du pivot de l'épaule (base_link -> joint2)
        self.L1 = 0.30           # Longueur du bras (Épaule -> Coude)
        self.L2 = 0.20           # Longueur de l'avant-bras (Coude -> Poignet)
        self.L3 = 0.075          # Distance Poignet -> Centre de la pince
        
        # Position initiale par défaut des articulations (Angles en radians)
        self.joint_positions = {
            "joint1": 0.0,
            "joint2": 0.0,
            "joint3": 0.0,
            "joint4": 0.0,
            "gripper_finger1_joint": 0.015,
            "gripper_finger2_joint": 0.015
        }
        
        # Configuration de l'adresse IP de l'ESP32 et de son port d'écoute UDP
        # Tu peux redéfinir l'IP dynamique par paramètre ROS au lancement, par défaut 192.168.1.100
        self.esp32_ip = rospy.get_param("~esp32_ip", "172.20.10.2") 
        self.esp32_port = rospy.get_param("~esp32_port", 4210)
        
        try:
            # Création du socket UDP IPv4
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Ne pas bloquer l'exécution de ROS si le réseau a de la latence
            self.udp_socket.settimeout(0.1)
            rospy.loginfo(f"[UDP] Client configure pour emettre vers {self.esp32_ip}:{self.esp32_port}")
        except Exception as e:
            rospy.logerr(f"[UDP] Impossible d'initialiser le socket réseau : {e}")
            self.udp_socket = None

        # Publisher pour mettre à jour l'affichage dans RViz
        self.joint_pub = rospy.Publisher("/joint_states", JointState, queue_size=10)
        
        # Serveur d'Interactive Markers
        self.server = InteractiveMarkerServer("robot_control_marker")
        self.menu_handler = MenuHandler()
        
        # Configuration du menu pour la pince
        self.menu_handler.insert("Ouvrir la pince", callback=self.open_gripper)
        self.menu_handler.insert("Fermer la pince", callback=self.close_gripper)

        # Création de l'unique marqueur interactif placé à l'organe terminal
        self.create_end_effector_marker()
        self.server.applyChanges()
        
        # Thread de publication continue des articulations et envoi UDP à 30Hz
        self.active = True
        self.pub_thread = threading.Thread(target=self.publish_loop)
        self.pub_thread.start()
        
        rospy.loginfo("Serveur de controle global par Organe Terminal (IK + UDP) pret !")

    def create_end_effector_marker(self):
        """ Crée l'unique marqueur interactif 6-DOF au bout du bras """
        int_marker = InteractiveMarker()
        int_marker.header.frame_id = "base_link"
        int_marker.name = "end_effector_target"
        int_marker.description = "Controleur Organe Terminal (IK)"
        int_marker.scale = 0.2
        
        # Position initiale du marqueur (bras légèrement déployé vers l'avant)
        int_marker.pose.position.x = 0.25
        int_marker.pose.position.y = 0.0
        int_marker.pose.position.z = 0.45
        int_marker.pose.orientation.w = 1.0

        # Représentation visuelle de la cible (une petite boîte orange translucide)
        visual_marker = Marker()
        visual_marker.type = Marker.CUBE
        visual_marker.scale.x = 0.05
        visual_marker.scale.y = 0.05
        visual_marker.scale.z = 0.05
        visual_marker.color.r = 1.0
        visual_marker.color.g = 0.5
        visual_marker.color.b = 0.0
        visual_marker.color.a = 0.7

        visual_control = InteractiveMarkerControl()
        visual_control.always_visible = True
        visual_control.markers.append(visual_marker)
        int_marker.controls.append(visual_control)

        # Contrôles de translation (X, Y, Z) et de rotation (Pitch)
        
        # Translation X
        control = InteractiveMarkerControl()
        control.name = "move_x"
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        control.orientation.w = 1.0
        control.orientation.x = 1.0
        int_marker.controls.append(control)

        # Translation Y
        control = InteractiveMarkerControl()
        control.name = "move_y"
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        control.orientation.w = 1.0
        control.orientation.z = 1.0
        int_marker.controls.append(control)

        # Translation Z
        control = InteractiveMarkerControl()
        control.name = "move_z"
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        control.orientation.w = 1.0
        control.orientation.y = 1.0
        int_marker.controls.append(control)

        # Rotation Y (Pitch - Inclinaison de la pince)
        control = InteractiveMarkerControl()
        control.name = "rotate_y"
        control.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        control.orientation.w = 1.0
        control.orientation.y = 1.0
        int_marker.controls.append(control)

        # Enregistrement du marqueur et association au callback et menu
        self.server.insert(int_marker, self.process_feedback)
        self.menu_handler.apply(self.server, "end_effector_target")

    def process_feedback(self, feedback):
        """ Calcule la cinématique inverse lorsque l'utilisateur manipule le marqueur """
        if feedback.event_type == feedback.POSE_UPDATE:
            # Récupération des coordonnées cibles cartésiennes du marqueur
            x = feedback.pose.position.x
            y = feedback.pose.position.y
            z = feedback.pose.position.z
            q = feedback.pose.orientation

            # 1. Calcul du Joint 1 (Rotation de la base autour de l'axe Z)
            theta1 = math.atan2(y, x)
            
            # Projection de la cible sur le plan vertical du bras (r, z)
            r = math.sqrt(x**2 + y**2)
            z_rel = z - self.shoulder_z  # Altitude relative par rapport à l'épaule

            # 2. Extraction du Pitch (angle d'inclinaison de la pince) depuis le quaternion du marqueur
            # sin(pitch) = 2.0 * (w*y - z*x)
            sin_pitch = 2.0 * (q.w * q.y - q.z * q.x)
            sin_pitch = max(-1.0, min(1.0, sin_pitch))  # Protection anti-NaN
            pitch = math.asin(sin_pitch)

            # 3. Calcul de la position théorique du poignet (joint 4)
            r_wrist = r - self.L3 * math.cos(pitch)
            z_wrist = z_rel - self.L3 * math.sin(pitch)

            # Distance Épaule -> Poignet
            D_sq = r_wrist**2 + z_wrist**2
            D = math.sqrt(D_sq)

            # Limiter la portée théorique pour éviter que le robot ne se disloque si on tire trop loin
            max_reach = self.L1 + self.L2
            if D > max_reach * 0.99:
                # Compression proportionnelle de la coordonnée cible vers la base
                scale = (max_reach * 0.99) / D
                r_wrist *= scale
                z_wrist *= scale
                D_sq = r_wrist**2 + z_wrist**2
                D = math.sqrt(D_sq)

            # Résolution de l'angle du Coude (Joint 3) via la loi des cosinus
            cos_theta3 = (D_sq - self.L1**2 - self.L2**2) / (2.0 * self.L1 * self.L2)
            cos_theta3 = max(-1.0, min(1.0, cos_theta3))  # Sécurité numérique
            
            # Configuration Coude en Haut (Elbow Up)
            theta3 = math.acos(cos_theta3)

            # Résolution de l'angle de l'Épaule (Joint 2)
            alpha = math.atan2(z_wrist, r_wrist)
            beta = math.atan2(self.L2 * math.sin(theta3), self.L1 + self.L2 * math.cos(theta3))
            theta2 = alpha - beta

            # Résolution de l'angle du Poignet (Joint 4) pour conserver l'orientation pitch voulue
            # La relation géométrique d'orientation plane est : pitch = theta2 + theta3 + theta4
            theta4 = pitch - theta2 - theta3

            # Limitation physique des articulations selon l'URDF pour éviter les postures impossibles
            self.joint_positions["joint1"] = max(-3.14, min(3.14, theta1))
            self.joint_positions["joint2"] = max(-1.57, min(1.57, theta2))
            self.joint_positions["joint3"] = max(-2.0, min(2.0, theta3))
            self.joint_positions["joint4"] = max(-1.57, min(1.57, theta4))

    def open_gripper(self, feedback):
        """ Ouvre la pince (via le menu contextuel) """
        rospy.loginfo("Ouverture de la pince")
        self.joint_positions["gripper_finger1_joint"] = 0.04
        self.joint_positions["gripper_finger2_joint"] = 0.04

    def close_gripper(self, feedback):
        """ Ferme la pince (via le menu contextuel) """
        rospy.loginfo("Fermeture de la pince")
        self.joint_positions["gripper_finger1_joint"] = 0.0
        self.joint_positions["gripper_finger2_joint"] = 0.0

    def publish_loop(self):
        """ Publication en continu à 30Hz """
        rate = rospy.Rate(30)
        while not rospy.is_shutdown() and self.active:
            # 1. Mise à jour de la visualisation ROS
            msg = JointState()
            msg.header.stamp = rospy.Time.now()
            msg.name = list(self.joint_positions.keys())
            msg.position = list(self.joint_positions.values())
            self.joint_pub.publish(msg)

            # 2. Transmission en UDP vers l'ESP32
            if self.udp_socket is not None:
                try:
                    # Construction de la trame CSV "j1,j2,j3,j4,g1,g2"
                    payload = (
                        f"{self.joint_positions['joint1']:.4f},"
                        f"{self.joint_positions['joint2']:.4f},"
                        f"{self.joint_positions['joint3']:.4f},"
                        f"{self.joint_positions['joint4']:.4f},"
                        f"{self.joint_positions['gripper_finger1_joint']:.4f},"
                        f"{self.joint_positions['gripper_finger2_joint']:.4f}"
                    )
                    # Envoi non bloquant vers l'ESP32
                    self.udp_socket.sendto(payload.encode("utf-8"), (self.esp32_ip, self.esp32_port))
                except Exception:
                    # On passe sous silence les erreurs réseaux temporaires pour ne pas saturer l'invite de commande
                    pass

            rate.sleep()

    def shutdown(self):
        self.active = False
        if hasattr(self, 'udp_socket') and self.udp_socket:
            try:
                self.udp_socket.close()
            except Exception:
                pass
        self.pub_thread.join()

if __name__ == "__main__":
    controller = RobotIKController()
    try:
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    finally:
        controller.shutdown()