#!/usr/bin/env python3
import rospy
import socket
import tf
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState, LaserScan
from std_msgs.msg import String
from geometry_msgs.msg import Quaternion
from math import sin, cos

UDP_IP = "0.0.0.0"
UDP_PORT_RECV = 12346 
ESP32_IP = "172.20.10.2" # <--- TON IP ESP32
ESP32_PORT_SEND = 12345

class RobotBrain:
    def __init__(self):
        rospy.init_node('esp32_odom_node')
        
        self.sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recv.bind((UDP_IP, UDP_PORT_RECV))
        self.sock_recv.setblocking(False)

        # Variables d'état
        self.auto_mode = False
        self.x, self.y, self.th = 0.0, 0.0, 0.0
        self.L, self.R = 0.25, 0.05
        self.last_enc_g, self.last_enc_d = 0.0, 0.0

        # ROS
        self.odom_pub = rospy.Publisher("/odom", Odometry, queue_size=50)
        self.joint_pub = rospy.Publisher("/joint_states", JointState, queue_size=50)
        self.tf_broadcaster = tf.TransformBroadcaster()
        
        rospy.Subscriber("/scan", LaserScan, self.lidar_callback)
        rospy.Subscriber("/robot_mode", String, self.mode_callback)

    def mode_callback(self, msg):
        self.auto_mode = (msg.data == "AUTO")
        rospy.loginfo(f"Mode changé en : {msg.data}")

    def lidar_callback(self, data):
        # Analyse du cône devant le robot
        front = data.ranges[0:20] + data.ranges[340:360]
        points = [d for d in front if d > 0.02]
        
        if points:
            min_dist = min(points)
            
            # --- COMPORTEMENT EN MODE AUTOMATIQUE ---
            if self.auto_mode:
                if min_dist < 0.25: # Si obstacle à 25cm, on tourne
                    rospy.loginfo("AUTO: Obstacle ! Rotation Gauche")
                    self.sock_send.sendto("3".encode(), (ESP32_IP, ESP32_PORT_SEND))
                else: # Sinon, on avance
                    self.sock_send.sendto("1".encode(), (ESP32_IP, ESP32_PORT_SEND))
            
            # --- SÉCURITÉ 5CM (Toujours active, même en manuel) ---
            elif min_dist < 0.06: # On met 6cm pour avoir une marge sur les 5cm
                rospy.logwarn(f"DANGER : Obstacle à {min_dist*100:.1f}cm ! STOP")
                self.sock_send.sendto("5".encode(), (ESP32_IP, ESP32_PORT_SEND))

    def run(self):
        while not rospy.is_shutdown():
            try:
                data, addr = self.sock_recv.recvfrom(1024)
                enc_g, enc_d = map(float, data.decode().split(','))
                
                # Odométrie
                dg, dd = enc_g - self.last_enc_g, enc_d - self.last_enc_d
                dist, dth = (dg + dd) / 2.0, (dd - dg) / self.L
                self.x += dist * cos(self.th)
                self.y += dist * sin(self.th)
                self.th += dth

                now = rospy.Time.now()
                odom_quat = tf.transformations.quaternion_from_euler(0, 0, self.th)

                # JointStates (Roues)
                js = JointState()
                js.header.stamp = now
                js.name = ['joint_rear_left_wheel', 'joint_front_left_wheel', 'joint_rear_right_wheel', 'joint_front_right_wheel']
                js.position = [enc_g/self.R, enc_g/self.R, enc_d/self.R, enc_d/self.R]
                self.joint_pub.publish(js)

                # TF & Odometry (Pour le SLAM)
                self.tf_broadcaster.sendTransform((self.x, self.y, 0), odom_quat, now, "base_link", "odom")
                
                o = Odometry()
                o.header.stamp, o.header.frame_id = now, "odom"
                o.child_frame_id = "base_link"
                o.pose.pose.position.x, o.pose.pose.position.y = self.x, self.y
                o.pose.pose.orientation = Quaternion(*odom_quat)
                self.odom_pub.publish(o)

                self.last_enc_g, self.last_enc_d = enc_g, enc_d
            except:
                continue
            rospy.sleep(0.01)

if __name__ == '__main__':
    RobotBrain().run()