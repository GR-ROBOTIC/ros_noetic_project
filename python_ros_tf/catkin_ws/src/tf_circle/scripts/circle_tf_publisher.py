#!/usr/bin/env python3

import rospy
import tf
import math

def main():
    rospy.init_node('circle_tf_publisher')

    br = tf.TransformBroadcaster()
    rate = rospy.Rate(30)  # 30 Hz

    radius = 1.0
    t = 0.0

    while not rospy.is_shutdown():

        # ========= AXE 1 =========
        x1 = radius * math.cos(t)
        y1 = 0.0
        z1 = radius * math.sin(t)

        br.sendTransform(
            (x1, y1, z1),
            tf.transformations.quaternion_from_euler(0, 0, 0),
            rospy.Time.now(),
            "axis_1",
            "world"
        )

        # ========= AXE 2 =========
        x2 = 0.5
        y2 = radius * math.sin(t)
        z2 = radius * math.cos(t)

        br.sendTransform(
            (x2, y2, z2),
            tf.transformations.quaternion_from_euler(0, 0, t),  # rotation
            rospy.Time.now(),
            "axis_2",
            "world"
        )

        t += 0.05
        rate.sleep()

if __name__ == '__main__':
    main()
