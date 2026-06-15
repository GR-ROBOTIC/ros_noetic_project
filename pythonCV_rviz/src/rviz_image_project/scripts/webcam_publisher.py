#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2

def main():
    rospy.init_node('webcam_publisher')

    image_pub = rospy.Publisher('/camera/image_raw', Image, queue_size=10)
    info_pub  = rospy.Publisher('/camera/camera_info', CameraInfo, queue_size=10)

    bridge = CvBridge()
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        rospy.logerr("Impossible d'ouvrir la webcam")
        return

    rate = rospy.Rate(30)

    while not rospy.is_shutdown():
        ret, frame = cap.read()
        if not ret:
            continue

        stamp = rospy.Time.now()

        # -------- Image --------
        img_msg = bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        img_msg.header.stamp = stamp
        img_msg.header.frame_id = "camera_frame"
        image_pub.publish(img_msg)

        # -------- CameraInfo --------
        info_msg = CameraInfo()
        info_msg.header.stamp = stamp
        info_msg.header.frame_id = "camera_frame"
        info_msg.width  = frame.shape[1]
        info_msg.height = frame.shape[0]

        # Matrice intrinsèque (factice mais valide)
        fx = 500.0
        fy = 500.0
        cx = info_msg.width / 2.0
        cy = info_msg.height / 2.0

        info_msg.K = [fx, 0.0, cx,
                      0.0, fy, cy,
                      0.0, 0.0, 1.0]

        info_msg.P = [fx, 0.0, cx, 0.0,
                      0.0, fy, cy, 0.0,
                      0.0, 0.0, 1.0, 0.0]

        info_pub.publish(info_msg)

        rate.sleep()

    cap.release()

if __name__ == '__main__':
    main()
