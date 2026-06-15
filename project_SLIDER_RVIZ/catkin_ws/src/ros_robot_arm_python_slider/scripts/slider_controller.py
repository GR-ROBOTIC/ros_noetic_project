#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import JointState
import tkinter as tk
import socket
import time

class JointSlider:
    """Classe pour un slider individuel"""
    def __init__(self, parent, name, min_val=0, max_val=180, axis='y', initial=0):
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.axis = axis
        self.value = initial

        frame = tk.Frame(parent, pady=5)
        frame.pack()
        tk.Label(frame, text=f"{self.name} (axis: {self.axis})").pack()
        self.slider = tk.Scale(frame, from_=self.min_val, to=self.max_val,
                               orient=tk.HORIZONTAL, length=300, resolution=1,
                               command=self.update_value)
        self.slider.set(initial)
        self.slider.pack()

    def update_value(self, val):
        self.value = float(val)

class RobotArmController:
    """Contrôle du robot + envoi TCP Wi-Fi vers ESP32"""
    def __init__(self, esp_ip="172.20.10.2", esp_port=5005):
        rospy.init_node("robot_arm_slider_controller")
        self.pub = rospy.Publisher("/joint_states", JointState, queue_size=10)

        self.root = tk.Tk()
        self.root.title("Robot Arm Slider Controller")

        # Définition des joints
        self.joint_definitions = [
            {"name": "base_joint", "min": 0, "max": 180, "axis": "z", "initial": 90},
            {"name": "A1_joint", "min": 0, "max": 180, "axis": "y", "initial": 45},
            {"name": "A2_joint", "min": 10, "max": 150, "axis": "y", "initial": 30},
            {"name": "A3_joint", "min": 0, "max": 180, "axis": "y", "initial": 60},
            {"name": "A4_joint", "min": 20, "max": 160, "axis": "y", "initial": 0}
        ]

        self.sliders = []
        for joint in self.joint_definitions:
            slider = JointSlider(self.root, joint["name"], joint["min"], joint["max"], joint["axis"], joint["initial"])
            self.sliders.append(slider)

        # Connexion TCP au ESP32
        self.esp_ip = esp_ip
        self.esp_port = esp_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        while not connected:
            try:
                self.sock.connect((self.esp_ip, self.esp_port))
                connected = True
                print(f"Connecté à ESP32 {self.esp_ip}:{self.esp_port}")
            except Exception as e:
                print(f"Erreur connexion ESP32, retry dans 2s: {e}")
                time.sleep(2)

        self.rate = rospy.Rate(20)  # 20 Hz
        self.loop()

    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = rospy.Time.now()
        msg.name = [s.name for s in self.sliders]
        msg.position = [s.value * 3.14159 / 180.0 for s in self.sliders]
        self.pub.publish(msg)

    def send_tcp(self):
        """Envoi des valeurs en temps réel à l'ESP32"""
        try:
            for s in self.sliders:
                message = f"{s.name}:{int(s.value)}\n"
                self.sock.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Erreur envoi TCP: {e}")

    def loop(self):
        while not rospy.is_shutdown():
            self.root.update()
            self.publish_joint_states()
            self.send_tcp()
            self.rate.sleep()

if __name__ == "__main__":
    try:
        RobotArmController(esp_ip="172.20.10.2", esp_port=5005)  # change l'IP ESP32
    except rospy.ROSInterruptException:
        pass