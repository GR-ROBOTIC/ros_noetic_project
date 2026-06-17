#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import rospy
import cv2
import math
import numpy as np
import struct
from pyzbar.pyzbar import decode
from visualization_msgs.msg import Marker
from sensor_msgs.msg import PointCloud2, PointField, JointState
import sensor_msgs.point_cloud2 as pc2
from std_msgs.msg import Header

def main():
    # --- Initialisation de ROS ---
    rospy.init_node('qrcode_vr_3d_screen', anonymous=True)
    
    # On publie directement les positions des articulations pour un mouvement instantané
    joint_pub = rospy.Publisher('/move_group/fake_controller_joint_states', JointState, queue_size=1)
    # Note : Si le robot ne bouge pas dans RViz, remplace par '/joint_states'
    
    # Publishers pour l'effet VR
    marker_pub = rospy.Publisher('/visualization_marker', Marker, queue_size=10)
    pc_pub = rospy.Publisher('/robot_vision/3d_screen', PointCloud2, queue_size=1)
    
    rospy.loginfo("📺 ÉCRAN 3D & CONTRÔLE DIRECT ACTIFS - Présentez le QR Code 1000.")

    cap = cv2.VideoCapture(0)

    # Résolution de l'écran virtuel 3D dans RViz
    SCREEN_W = 120
    SCREEN_H = 90
    
    # Angles par défaut du robot au démarrage (bras au repos)
    angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    while not rospy.is_shutdown() and cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.flip(image, 1)
        h, w, _ = image.shape
        
        # --- DÉTECTION DU QR CODE 1000 ---
        qr_codes = decode(image)
        
        for qr in qr_codes:
            qr_data = qr.data.decode('utf-8').strip()
            points_qr = qr.polygon
            
            if len(points_qr) == 4 and qr_data == "1000":
                cx = int(np.mean([pt.x for pt in points_qr]))
                cy = int(np.mean([pt.y for pt in points_qr]))
                
                # Dessin du contour vert
                pts = np.array([[pt.x, pt.y] for pt in points_qr], np.int32)
                cv2.polylines(image, [pts], True, (0, 255, 0), 3)
                cv2.circle(image, (cx, cy), 7, (0, 255, 0), -1)
                
                # Calcul de la position de la cible pour RViz
                target_y = (cx / w - 0.5) * -0.6    
                target_z = (0.5 - cy / h) * 0.5 + 0.3 
                largeur_qr = np.linalg.norm(np.array([points_qr[0].x, points_qr[0].y]) - np.array([points_qr[1].x, points_qr[1].y]))
                target_x = max(0.2, min(0.6, 150.0 / (largeur_qr + 1.0))) 

                # Publication de la sphère verte de ciblage dans RViz
                marker = Marker()
                marker.header.frame_id = "base_link"
                marker.header.stamp = rospy.Time.now()
                marker.ns = "qrcode_target"
                marker.id = 0
                marker.type = Marker.SPHERE
                marker.action = Marker.ADD
                marker.pose.position.x = target_x
                marker.pose.position.y = target_y
                marker.pose.position.z = target_z
                marker.scale.x = 0.05
                marker.scale.y = 0.05
                marker.scale.z = 0.05
                marker.color.r = 0.0; marker.color.g = 1.0; marker.color.b = 0.0; marker.color.a = 0.9
                marker_pub.publish(marker)

                # --- CALCUL ET CONVERSION DES ANGLES ---
                # Pivot de la base (Axe X/Y)
                angle_waist = math.atan2(target_y, target_x)
                
                # Hauteur de l'épaule (Axe Z)
                angle_shoulder = (cy / h - 0.5) * -1.5
                
                # Application des limites pour éviter que le robot ne force
                angle_waist = max(min(angle_waist, 3.14), -3.14)
                angle_shoulder = max(min(angle_shoulder, 1.57), -1.57)

                # Mise à jour des articulations
                angles = [angle_waist, angle_shoulder, 0.0, 0.0, 0.0, 0.0]

        # --- ENVOI DE LA COMMANDE DE POSITION AU ROBOT ---
        joint_state = JointState()
        joint_state.header = Header()
        joint_state.header.stamp = rospy.Time.now()
        # /!\ Pense à remplacer ces noms par ceux exacts de ton URDF si nécessaire
        joint_state.name = ['waist_joint', 'shoulder_joint', 'elbow_joint', 'wrist_joint', 'joint_5', 'joint_6']
        joint_state.position = angles
        joint_pub.publish(joint_state)

        # --- CRÉATION DE L'ÉCRAN TEXTURÉ 3D DANS RVIZ ---
        small_img = cv2.resize(image, (SCREEN_W, SCREEN_H))
        points = []
        
        for v in range(SCREEN_H):
            for u in range(SCREEN_W):
                x_pixel = 0.6 
                y_pixel = (u / SCREEN_W - 0.5) * -0.8 
                z_pixel = (0.5 - v / SCREEN_H) * 0.6 + 0.4 
                
                b, g, r = small_img[v, u]
                rgb = struct.unpack('I', struct.pack('BBBB', b, g, r, 0))[0]
                points.append([x_pixel, y_pixel, z_pixel, rgb])
        
        fields = [
            PointField('x', 0, PointField.FLOAT32, 1),
            PointField('y', 4, PointField.FLOAT32, 1),
            PointField('z', 8, PointField.FLOAT32, 1),
            PointField('rgb', 12, PointField.UINT32, 1)
        ]
        
        header = Header(frame_id="base_link", stamp=rospy.Time.now())
        pc_msg = pc2.create_cloud(header, fields, points)
        pc_pub.publish(pc_msg)
        
        # Affichage local (Optionnel, évite les bugs Qt)
        cv2.imshow("Vision - Flux Local", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()