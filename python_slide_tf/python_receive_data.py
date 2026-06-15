#!/usr/bin/env python3
import rospy
import tf
import socket
import math

class TFSocket:
    def __init__(self, host='0.0.0.0', port=5005):
        rospy.init_node('tf_socket_pub')
        self.br = tf.TransformBroadcaster()

        # Paramètres réseau
        self.host = host
        self.port = port

        # Créer un socket TCP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        rospy.loginfo(f"En attente de connexion ESP32 sur {self.host}:{self.port}...")
        self.conn, addr = self.sock.accept()
        rospy.loginfo(f"Connecté à {addr}")

        # Valeurs initiales
        self.link1 = 0.0
        self.link2 = 0.0
        self.link3 = 0.0
        self.link4_rot = 0.0
        self.global_x = 0.0
        self.extra = 0.0

        # Boucle de publication TF
        self.rate = rospy.Rate(20)
        self.run()

    def run(self):
        while not rospy.is_shutdown():
            # Lire les données envoyées par l'ESP32
            try:
                data = self.conn.recv(1024).decode('utf-8').strip()
                if data:
                    # Exemple de format attendu : "0.1,0.2,-0.1,45,0.5,0.0"
                    values = data.split(',')
                    if len(values) == 6:
                        self.link1 = float(values[0])
                        self.link2 = float(values[1])
                        self.link3 = float(values[2])
                        self.link4_rot = float(values[3])
                        self.global_x = float(values[4])
                        self.extra = float(values[5])  # tu peux l'utiliser comme tu veux
                    else:
                        rospy.logwarn("Données reçues incorrectes (attendu 6 valeurs)")

            except Exception as e:
                rospy.logwarn(f"Erreur socket: {e}")
                continue

            # --------- Publier TF ---------
            # Link1
            self.br.sendTransform(
                (self.link1 + self.global_x, 0, 0),
                tf.transformations.quaternion_from_euler(0, 0, 0),
                rospy.Time.now(),
                "link1",
                "base_link"
            )

            # Link2
            self.br.sendTransform(
                (self.link2 + self.global_x, 0, 0),
                tf.transformations.quaternion_from_euler(0, 0, 0),
                rospy.Time.now(),
                "link2",
                "base_link"
            )

            # Link3
            self.br.sendTransform(
                (self.link3 + self.global_x, 0, 0),
                tf.transformations.quaternion_from_euler(0, 0, 0),
                rospy.Time.now(),
                "link3",
                "base_link"
            )

            # Link4 rotation Z
            angle_rad = math.radians(self.link4_rot)
            self.br.sendTransform(
                (self.global_x, 0, 0),
                tf.transformations.quaternion_from_euler(0, 0, angle_rad),
                rospy.Time.now(),
                "link4",
                "base_link"
            )

            self.rate.sleep()


if __name__ == "__main__":
    try:
        TFSocket()
    except rospy.ROSInterruptException:
        pass
