#!/usr/bin/env python3
import rospy
import socket
import tf
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState, LaserScan
from std_msgs.msg import String
from geometry_msgs.msg import Quaternion
from math import sin, cos, pi

# --- CONFIGURATION RÉSEAU ---
UDP_IP = "0.0.0.0"
UDP_PORT_RECV = 12346 
ESP32_IP = "172.20.10.2" # <--- METS L'IP DE TON ESP32 ICI
ESP32_PORT_SEND = 12345

# --- PARAMÈTRES PHYSIQUES DU ROBOT ---
TICKS_PER_REV = 20.0   
WHEEL_RADIUS = 0.033   
WHEEL_BASE = 0.18      
METERS_PER_TICK = (2 * pi * WHEEL_RADIUS) / TICKS_PER_REV

# --- CORRECTION DES SIGNES ---
# Inversion des deux pour corriger Avancer/Reculer ET Gauche/Droite
FIX_ENCODER_G = 1   # Changé de -1 à 1
FIX_ENCODER_D = -1  # Changé de 1 à -1

class RobotBrain:
    def __init__(self):
        rospy.init_node('esp32_odom_node')
        
        self.sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recv.bind((UDP_IP, UDP_PORT_RECV))
        self.sock_recv.setblocking(False)

        self.auto_mode = False
        self.x, self.y, self.th = 0.0, 0.0, 0.0
        self.last_enc_g, self.last_enc_d = 0.0, 0.0
        self.first_data = True

        self.odom_pub = rospy.Publisher("/odom", Odometry, queue_size=10)
        self.joint_pub = rospy.Publisher("/joint_states", JointState, queue_size=10)
        self.tf_broadcaster = tf.TransformBroadcaster()
        
        rospy.Subscriber("/scan", LaserScan, self.lidar_callback)
        rospy.Subscriber("/robot_mode", String, self.mode_callback)

    def mode_callback(self, msg):
        self.auto_mode = (msg.data == "AUTO")

    def lidar_callback(self, data):
        front_ranges = data.ranges[0:15] + data.ranges[345:360]
        points = [d for d in front_ranges if d > 0.02]
        if points:
            min_dist = min(points)
            if min_dist < 0.06: 
                self.sock_send.sendto("5".encode(), (ESP32_IP, ESP32_PORT_SEND))
            elif self.auto_mode:
                if min_dist < 0.30: 
                    self.sock_send.sendto("3".encode(), (ESP32_IP, ESP32_PORT_SEND))
                else:
                    self.sock_send.sendto("1".encode(), (ESP32_IP, ESP32_PORT_SEND))

    def run(self):
        rospy.loginfo("Odométrie : Signes inversés pour corriger la direction.")
        while not rospy.is_shutdown():
            try:
                data, addr = self.sock_recv.recvfrom(1024)
                raw_g, raw_d = map(float, data.decode().split(','))
                
                # Application des nouveaux signes correctifs
                enc_g = raw_g * FIX_ENCODER_G
                enc_d = raw_d * FIX_ENCODER_D
                
                if self.first_data:
                    self.last_enc_g, self.last_enc_d = enc_g, enc_d
                    self.first_data = False
                    continue

                # Calcul des deltas (en mètres)
                d_left = (enc_g - self.last_enc_g) * METERS_PER_TICK
                d_right = (enc_d - self.last_enc_d) * METERS_PER_TICK

                # Calcul du déplacement
                dist = (d_right + d_left) / 2.0
                d_th = (d_right - d_left) / WHEEL_BASE

                # Mise à jour de la position globale
                self.x += dist * cos(self.th)
                self.y += dist * sin(self.th)
                self.th += d_th

                now = rospy.Time.now()
                odom_quat = tf.transformations.quaternion_from_euler(0, 0, self.th)

                # 1. TF odom -> base_link
                self.tf_broadcaster.sendTransform((self.x, self.y, 0), odom_quat, now, "base_link", "odom")
                
                # 2. Message Odometry
                o = Odometry()
                o.header.stamp, o.header.frame_id = now, "odom"
                o.child_frame_id = "base_link"
                o.pose.pose.position.x, o.pose.pose.position.y = self.x, self.y
                o.pose.pose.orientation = Quaternion(*odom_quat)
                self.odom_pub.publish(o)

                # 3. Message JointStates
                js = JointState()
                js.header.stamp = now
                js.name = ['joint_rear_left_wheel', 'joint_front_left_wheel', 'joint_rear_right_wheel', 'joint_front_right_wheel']
                pos_g, pos_d = enc_g * (2*pi/TICKS_PER_REV), enc_d * (2*pi/TICKS_PER_REV)
                js.position = [pos_g, pos_g, pos_d, pos_d]
                self.joint_pub.publish(js)

                self.last_enc_g, self.last_enc_d = enc_g, enc_d

            except:
                continue
            rospy.sleep(0.01)

if __name__ == '__main__':
    RobotBrain().run()