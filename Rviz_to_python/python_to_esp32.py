#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import tf2_ros
import geometry_msgs.msg
import socket
from interactive_markers.interactive_marker_server import InteractiveMarkerServer
from visualization_msgs.msg import InteractiveMarker, InteractiveMarkerControl

ESP32_IP = "172.20.10.4"  # Adresse IP de l'ESP32
ESP32_PORT = 5005           # Port UDP choisi

class TFInteractiveNode:

    def __init__(self):
        rospy.init_node("tf_interactive_node")

        # ===== UDP socket =====
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # ===== Paramètre ROS =====
        self.print_values = rospy.get_param("~print_tf_values", True)

        # ===== TF Broadcaster =====
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()

        # ===== Données de position =====
        self.tf_data = {
            "tf1": [0.0, 0.0, 0.0],
            "tf2": [1.0, 0.0, 0.0],
            "tf3": [0.0, 1.0, 0.0],
            "tf4": [1.0, 1.0, 0.0],
        }

        # ===== Données de rotation (tf2 & tf3 seulement) =====
        self.tf_rotation = {
            "tf2": [0.0, 0.0, 0.0, 1.0],
            "tf3": [0.0, 0.0, 0.0, 1.0],
        }

        # ===== Variables explicites TF3 et TF4 =====
        self.tf3x = 0.0
        self.tf3y = 0.0
        self.tf3z = 0.0
        self.tf4x = 0.0
        self.tf4y = 0.0
        self.tf4z = 0.0

        # ===== Interactive Marker Server =====
        self.server = InteractiveMarkerServer("tf_markers")
        for name in self.tf_data:
            self.create_marker(name)
        self.server.applyChanges()

        # ===== Timer TF =====
        rospy.Timer(rospy.Duration(0.05), self.publish_tf)

        rospy.loginfo("TF Interactive Node with UDP started")
        rospy.spin()

    # =========================
    # Création Marker
    # =========================
    def create_marker(self, name):
        marker = InteractiveMarker()
        marker.header.frame_id = "world"
        marker.name = name
        marker.description = name
        marker.scale = 0.4

        marker.pose.position.x = self.tf_data[name][0]
        marker.pose.position.y = self.tf_data[name][1]
        marker.pose.position.z = self.tf_data[name][2]
        marker.pose.orientation.w = 1.0

        self.add_move_axis(marker, "x", 1, 0, 0)
        self.add_move_axis(marker, "y", 0, 1, 0)
        self.add_move_axis(marker, "z", 0, 0, 1)

        if name in ["tf2", "tf3"]:
            self.add_rotate_axis(marker, "rot_x", 1, 0, 0)
            self.add_rotate_axis(marker, "rot_y", 0, 1, 0)
            self.add_rotate_axis(marker, "rot_z", 0, 0, 1)

        self.server.insert(marker, self.process_feedback)

    def add_move_axis(self, marker, axis, ox, oy, oz):
        ctrl = InteractiveMarkerControl()
        ctrl.name = f"move_{axis}"
        ctrl.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        ctrl.orientation.w = 1.0
        ctrl.orientation.x = ox
        ctrl.orientation.y = oy
        ctrl.orientation.z = oz
        marker.controls.append(ctrl)

    def add_rotate_axis(self, marker, name, ox, oy, oz):
        ctrl = InteractiveMarkerControl()
        ctrl.name = name
        ctrl.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        ctrl.orientation.w = 1.0
        ctrl.orientation.x = ox
        ctrl.orientation.y = oy
        ctrl.orientation.z = oz
        marker.controls.append(ctrl)

    # =========================
    # Callback RViz
    # =========================
    def process_feedback(self, feedback):
        name = feedback.marker_name
        self.tf_data[name][0] = feedback.pose.position.x
        self.tf_data[name][1] = feedback.pose.position.y
        self.tf_data[name][2] = feedback.pose.position.z

        if name in ["tf2", "tf3"]:
            self.tf_rotation[name] = [
                feedback.pose.orientation.x,
                feedback.pose.orientation.y,
                feedback.pose.orientation.z,
                feedback.pose.orientation.w,
            ]

        if name == "tf3":
            self.tf3x = feedback.pose.position.x
            self.tf3y = feedback.pose.position.y
            self.tf3z = feedback.pose.position.z

        if name == "tf4":
            self.tf4x = feedback.pose.position.x
            self.tf4y = feedback.pose.position.y
            self.tf4z = feedback.pose.position.z

        # Affichage console
        if self.print_values:
            print(f"[VAR] tf3 -> x:{self.tf3x:.3f}, y:{self.tf3y:.3f}, z:{self.tf3z:.3f}")
            print(f"[VAR] tf4 -> x:{self.tf4x:.3f}, y:{self.tf4y:.3f}, z:{self.tf4z:.3f}")

        self.server.applyChanges()

        # Envoi UDP vers ESP32
        self.send_udp()

    # =========================
    # Envoi UDP
    # =========================
    def send_udp(self):
        message = f"{self.tf3x},{self.tf3y},{self.tf3z},{self.tf4x},{self.tf4y},{self.tf4z}"
        self.sock.sendto(message.encode(), (ESP32_IP, ESP32_PORT))

    # =========================
    # Publication TF ROS
    # =========================
    def publish_tf(self, event):
        for name, pos in self.tf_data.items():
            t = geometry_msgs.msg.TransformStamped()
            t.header.stamp = rospy.Time.now()
            t.header.frame_id = "world"
            t.child_frame_id = name

            t.transform.translation.x = pos[0]
            t.transform.translation.y = pos[1]
            t.transform.translation.z = pos[2]

            if name in ["tf2", "tf3"]:
                t.transform.rotation.x = self.tf_rotation[name][0]
                t.transform.rotation.y = self.tf_rotation[name][1]
                t.transform.rotation.z = self.tf_rotation[name][2]
                t.transform.rotation.w = self.tf_rotation[name][3]
            else:
                t.transform.rotation.x = 0.0
                t.transform.rotation.y = 0.0
                t.transform.rotation.z = 0.0
                t.transform.rotation.w = 1.0

            self.tf_broadcaster.sendTransform(t)


if __name__ == "__main__":
    TFInteractiveNode()
