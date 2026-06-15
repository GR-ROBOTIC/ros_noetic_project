#!/usr/bin/env python3
import rospy
import tf
import tkinter as tk
import math

class TFSlider:
    def __init__(self):
        # Initialisation du noeud ROS
        rospy.init_node('tf_slider_pub')
        self.br = tf.TransformBroadcaster()

        # Création de la fenêtre Tkinter
        self.root = tk.Tk()
        self.root.title("TF Sliders")

        # ---------- Sliders individuels ----------
        # Link 1 X
        self.x1 = tk.DoubleVar()
        tk.Scale(self.root, variable=self.x1, from_=-1.0, to=1.0,
                 resolution=0.01, orient=tk.HORIZONTAL, length=400,
                 label="Link 1 X (Rouge)").pack()

        # Link 2 X
        self.x2 = tk.DoubleVar()
        tk.Scale(self.root, variable=self.x2, from_=-1.0, to=1.0,
                 resolution=0.01, orient=tk.HORIZONTAL, length=400,
                 label="Link 2 X (Vert)").pack()

        # Link 3 X
        self.x3 = tk.DoubleVar()
        tk.Scale(self.root, variable=self.x3, from_=-1.0, to=1.0,
                 resolution=0.01, orient=tk.HORIZONTAL, length=400,
                 label="Link 3 X (Jaune)").pack()

        # Link 4 rotation Z
        self.rot_z = tk.DoubleVar()
        tk.Scale(self.root, variable=self.rot_z, from_=-180, to=180,
                 resolution=1, orient=tk.HORIZONTAL, length=400,
                 label="Link 4 rotation Z (Violet)").pack()

        # ---------- 5ème slider global ----------
        self.global_slide = tk.DoubleVar()
        tk.Scale(self.root, variable=self.global_slide, from_=-1.0, to=1.0,
                 resolution=0.01, orient=tk.HORIZONTAL, length=400,
                 label="Déplacement global X").pack()

        # Lancement de la boucle de mise à jour
        self.update()
        self.root.mainloop()

    def update(self):
        # Valeur du slider global
        global_offset = self.global_slide.get()

        # ---------- Link 1 ----------
        x1_pos = self.x1.get() + global_offset
        self.br.sendTransform(
            (x1_pos, 0, 0),
            tf.transformations.quaternion_from_euler(0, 0, 0),
            rospy.Time.now(),
            "link1",
            "base_link"
        )

        # ---------- Link 2 ----------
        x2_pos = self.x2.get() + global_offset
        self.br.sendTransform(
            (x2_pos, 0, 0),
            tf.transformations.quaternion_from_euler(0, 0, 0),
            rospy.Time.now(),
            "link2",
            "base_link"
        )

        # ---------- Link 3 ----------
        x3_pos = self.x3.get() + global_offset
        self.br.sendTransform(
            (x3_pos, 0, 0),
            tf.transformations.quaternion_from_euler(0, 0, 0),
            rospy.Time.now(),
            "link3",
            "base_link"
        )

        # ---------- Link 4 (rotation Z) ----------
        angle_z_rad = math.radians(self.rot_z.get())
        self.br.sendTransform(
            (global_offset, 0, 0),  # appliquer translation globale
            tf.transformations.quaternion_from_euler(0, 0, angle_z_rad),
            rospy.Time.now(),
            "link4",
            "base_link"
        )

        # Appel récursif toutes les 50ms
        self.root.after(50, self.update)


if __name__ == "__main__":
    TFSlider()
