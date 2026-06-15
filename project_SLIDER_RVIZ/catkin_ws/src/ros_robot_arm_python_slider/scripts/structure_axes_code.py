#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import JointState
import tkinter as tk
import socket
import threading
import json
import time

class JointSlider:
    def __init__(self, parent, name, min_val=0, max_val=180, axis='y', initial=0):
        self.name = name
        self.value = initial
        frame = tk.Frame(parent, pady=5)
        frame.pack()
        tk.Label(frame, text=f"{self.name} (axis: {axis})").pack()
        self.slider = tk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, length=300,
                               resolution=1, command=self.update_value)
        self.slider.set(initial)
        self.slider.pack()

    def update_value(self, val):
        self.value = float(val)

class RobotArmController:
    def __init__(self, esp_ip="172.20.10.2", esp_port=5005, send_rate=20):
        rospy.init_node("robot_arm_slider_controller")
        self.pub = rospy.Publisher("/joint_states", JointState, queue_size=10)
        self.root = tk.Tk()
        self.root.title("Robot Arm Slider Controller")

        # Définition des joints
        self.joint_defs = [
            {"name":"base","min":0,"max":180,"initial":90},
            {"name":"A1","min":0,"max":180,"initial":45},
            {"name":"A2","min":10,"max":150,"initial":30},
            {"name":"A3","min":0,"max":180,"initial":60},
            {"name":"A4","min":20,"max":160,"initial":0}
        ]

        self.sliders = [JointSlider(self.root, j["name"], j["min"], j["max"], initial=j["initial"]) for j in self.joint_defs]

        # TCP
        self.esp_ip = esp_ip
        self.esp_port = esp_port
        self.send_rate = send_rate
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.connect_tcp()

        # Thread pour envoi continu
        self.running = True
        self.thread = threading.Thread(target=self.send_loop)
        self.thread.daemon = True
        self.thread.start()

        self.rate = rospy.Rate(20)
        self.loop()

    def connect_tcp(self):
        while not self.connected and not rospy.is_shutdown():
            try:
                print(f"Tentative connexion à ESP32 {self.esp_ip}:{self.esp_port} ...")
                self.sock.connect((self.esp_ip, self.esp_port))
                self.connected = True
                print("Connecté !")
            except Exception as e:
                print(f"Échec connexion, retry 2s: {e}")
                time.sleep(2)

    def get_values(self):
        return {s.name: int(s.value) for s in self.sliders}

    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = rospy.Time.now()
        msg.name = [s.name for s in self.sliders]
        msg.position = [s.value*3.14159/180.0 for s in self.sliders]
        self.pub.publish(msg)

    def send_loop(self):
        while self.running:
            if self.connected:
                try:
                    data = self.get_values()
                    msg = json.dumps(data) + "\n"
                    self.sock.sendall(msg.encode('utf-8'))
                except (BrokenPipeError, ConnectionResetError):
                    print("Connexion perdue, tentative de reconnexion...")
                    self.connected = False
                    self.sock.close()
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.connect_tcp()
            time.sleep(1/self.send_rate)

    def loop(self):
        try:
            while not rospy.is_shutdown():
                self.root.update()
                self.publish_joint_states()
                self.rate.sleep()
        except tk.TclError:
            self.running = False
            self.sock.close()

if __name__ == "__main__":
    RobotArmController(esp_ip="172.20.10.2", esp_port=5005)