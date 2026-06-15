#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import tf2_ros
import geometry_msgs.msg
import socket
from interactive_markers.interactive_marker_server import InteractiveMarkerServer
from visualization_msgs.msg import InteractiveMarker, InteractiveMarkerControl

class TFInteractiveNode:

    def __init__(self):
        rospy.init_node("tf_interactive_node")

        # Paramètre pour afficher les valeurs
        self.print_values = rospy.get_param("~print_tf_values", True)

        # UDP
        self.udp_ip = rospy.get_param("~udp_ip", "127.0.0.1")
        self.udp_port = rospy.get_param("~udp_port", 5005)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rospy.loginfo(f"UDP activé vers {self.udp_ip}:{self.udp_port}")

        # TF broadcaster
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()

        # TF data – on ne prend que 3 TF
        self.tf_data = {
            "tf1": [0.0, 0.0, 0.0],
            "tf2": [1.0, 0.0, 0.0],
            "tf3": [0.0, 1.0, 0.0],
        }

        # Interactive Marker Server
        self.server = InteractiveMarkerServer("tf_markers")
        for name in self.tf_data:
            self.create_marker(name)
        self.server.applyChanges()

        # Timer pour publier TF
        rospy.Timer(rospy.Duration(0.05), self.publish_tf)
        rospy.spin()

    # =========================
    # Création d’un marker interactif
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

        # Ajouter axes
        self.add_axis(marker, "x", 1, 0, 0)
        self.add_axis(marker, "y", 0, 1, 0)
        self.add_axis(marker, "z", 0, 0, 1)

        self.server.insert(marker, self.feedback_cb)

    def add_axis(self, marker, axis, ox, oy, oz):
        ctrl = InteractiveMarkerControl()
        ctrl.name = f"move_{axis}"
        ctrl.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        ctrl.orientation.w = 1
        ctrl.orientation.x = ox
        ctrl.orientation.y = oy
        ctrl.orientation.z = oz
        marker.controls.append(ctrl)    

    # =========================
    # Feedback RViz
    # =========================
    def feedback_cb(self, feedback):
        name = feedback.marker_name
        x = feedback.pose.position.x
        y = feedback.pose.position.y
        z = feedback.pose.position.z

        self.tf_data[name] = [x, y, z]

        if self.print_values:
            print(f"{name} -> Valeur 1 : {x:.3f} | Valeur 2 : {y:.3f} | Valeur 3 : {z:.3f}")

        # Envoi UDP pour **les 3 TF à la fois**
        self.send_udp_all()

        self.server.applyChanges()

    # =========================
    # Envoi UDP de tous les TF
    # =========================
    def send_udp_all(self):
        try:
            # Format : tf1_x,tf1_y,tf1_z,tf2_x,tf2_y,tf2_z,tf3_x,tf3_y,tf3_z
            values = []
            for name in ["tf1", "tf2", "tf3"]:
                values.extend([f"{v:.3f}" for v in self.tf_data[name]])

            msg = ",".join(values) + "\n"
            self.sock.sendto(msg.encode("utf-8"), (self.udp_ip, self.udp_port))
        except Exception as e:
            rospy.logerr(f"Erreur UDP: {e}")

    # =========================
    # Publication TF
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
            t.transform.rotation.w = 1.0
            self.tf_broadcaster.sendTransform(t)


if __name__ == "__main__":
    TFInteractiveNode()
