#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import rospy
import moveit_commander
import math
from sensor_msgs.msg import JointState

def to_360(rad):
    deg = math.degrees(rad) % 360
    return deg if deg >= 0 else deg + 360

def callback(msg):
    rospy.loginfo("=== Positions (0-360°) ===")
    for name, pos in zip(msg.name, msg.position):
        rospy.loginfo(f"Axe [{name}] : {to_360(pos):.2f}°")

def main():
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('robot_commander', anonymous=True)
    
    group_name = "arm"
    arm = moveit_commander.MoveGroupCommander(group_name)
    
    rospy.Subscriber("/joint_states", JointState, callback)
    
    rospy.sleep(2)
    rospy.loginfo("Envoi du robot 4-axes vers sa cible...")
    
    target = [math.radians(90), math.radians(45), math.radians(-30), 0]
    
    try:
        arm.go(target, wait=True)
        arm.stop()
        rospy.loginfo("Mouvement reussi !")
    except Exception as e:
        rospy.logerr(f"Erreur de mouvement : {e}")
    
    rospy.spin()

if __name__ == '__main__':
    main()