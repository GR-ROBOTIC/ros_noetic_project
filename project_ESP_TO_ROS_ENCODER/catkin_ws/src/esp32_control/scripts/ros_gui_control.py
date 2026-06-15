#!/usr/bin/env python3
import tkinter as tk
import socket
import rospy
from std_msgs.msg import String

# --- CONFIGURATION (Gardée à l'identique) ---
ESP32_IP = "172.20.10.2" 
ESP32_PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class RobotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Dashboard")
        self.root.geometry("350x500")
        self.root.configure(bg="#2c3e50") # Bleu nuit moderne
        
        rospy.init_node('gui_node')
        self.mode_pub = rospy.Publisher('/robot_mode', String, queue_size=10)
        self.auto_mode = False

        # --- STYLE DES BOUTONS ---
        # On définit un dictionnaire pour ne pas répéter le code
        btn_style = {
            "font": ("Helvetica", 10, "bold"),
            "fg": "white",
            "width": 8,
            "height": 3,
            "relief": "flat",
            "activebackground": "#34495e"
        }

        # --- TITRE ---
        tk.Label(root, text="CONTROL PANEL", bg="#2c3e50", fg="#ecf0f1", 
                 font=("Helvetica", 12, "bold"), pady=15).pack()

        # --- BOUTON MODE (AUTO/MANUEL) ---
        self.btn_mode = tk.Button(root, text="MODE: MANUEL", bg="#7f8c8d", 
                                 command=self.toggle_mode, font=("Helvetica", 10, "bold"),
                                 fg="white", width=20, height=2, relief="flat")
        self.btn_mode.pack(pady=10)

        # --- GRILLE DE CONTROLE (D-PAD) ---
        frame_ctrl = tk.Frame(root, bg="#2c3e50")
        frame_ctrl.pack(pady=20)

        # Bouton AVANT (1)
        tk.Button(frame_ctrl, text="▲", bg="#3498db", **btn_style, 
                  command=lambda: self.send("1")).grid(row=0, column=1, padx=5, pady=5)

        # Bouton GAUCHE (3)
        tk.Button(frame_ctrl, text="◀", bg="#3498db", **btn_style, 
                  command=lambda: self.send("3")).grid(row=1, column=0, padx=5, pady=5)

        # Bouton STOP (5)
        tk.Button(frame_ctrl, text="STOP", bg="#e74c3c", **btn_style, 
                  command=lambda: self.send("5")).grid(row=1, column=1, padx=5, pady=5)

        # Bouton DROITE (4)
        tk.Button(frame_ctrl, text="▶", bg="#3498db", **btn_style, 
                  command=lambda: self.send("4")).grid(row=1, column=2, padx=5, pady=5)

        # Bouton ARRIERE (2)
        tk.Button(frame_ctrl, text="▼", bg="#3498db", **btn_style, 
                  command=lambda: self.send("2")).grid(row=2, column=1, padx=5, pady=5)

    def send(self, cmd):
        # Logique identique : on n'envoie que si on est en manuel
        if not self.auto_mode:
            sock.sendto(cmd.encode(), (ESP32_IP, ESP32_PORT))

    def toggle_mode(self):
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            self.btn_mode.config(text="MODE: AUTOMATIQUE", bg="#27ae60") # Vert
            self.mode_pub.publish("AUTO")
        else:
            self.btn_mode.config(text="MODE: MANUEL", bg="#7f8c8d") # Gris
            self.mode_pub.publish("MANUEL")
            self.send("5") # Stop de sécurité

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotGUI(root)
    root.mainloop()