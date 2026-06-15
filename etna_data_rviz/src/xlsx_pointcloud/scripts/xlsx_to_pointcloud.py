#!/usr/bin/env python3
import rospy
import pandas as pd
import sensor_msgs.point_cloud2 as pc2
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header

def main():
    rospy.init_node("xlsx_pointcloud_node")

    pub = rospy.Publisher("/temperature_cloud", PointCloud2, queue_size=1)

    # Charger le fichier Excel
    file_path = rospy.get_param("~file_path")
    df = pd.read_excel(file_path)

    temperatures = df["param_int (AVG)"].values

    points = []
    rate = rospy.Rate(2)  # vitesse d'animation (2 points/sec)

    for i, temp in enumerate(temperatures):
        if rospy.is_shutdown():
            break

        # X = temps (index), Y = 0, Z = température
        points.append((float(i), 0.0, float(temp)))

        header = Header()
        header.stamp = rospy.Time.now()
        header.frame_id = "map"

        fields = [
            PointField("x", 0, PointField.FLOAT32, 1),
            PointField("y", 4, PointField.FLOAT32, 1),
            PointField("z", 8, PointField.FLOAT32, 1),
        ]

        cloud = pc2.create_cloud(header, fields, points)
        pub.publish(cloud)

        rate.sleep()

    rospy.loginfo("Tous les points ont été publiés.")

if __name__ == "__main__":
    main()
