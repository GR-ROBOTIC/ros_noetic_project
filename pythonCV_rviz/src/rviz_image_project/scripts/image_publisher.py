#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

def main():
    rospy.init_node('webcam_publisher', anonymous=True)

    pub = rospy.Publisher('/camera/image_raw', Image, queue_size=10)
    bridge = CvBridge()

    # Ouvre la webcam (0 = webcam par défaut)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        rospy.logerr("Impossible d'ouvrir la webcam")
        return

    rate = rospy.Rate(30)  # 30 FPS

    while not rospy.is_shutdown():
        ret, frame = cap.read()
        if not ret:
            rospy.logwarn("Image webcam non reçue")
            continue

        # Conversion OpenCV -> ROS
        msg = bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        pub.publish(msg)

        rate.sleep()

    cap.release()

if __name__ == '__main__':
    main()
