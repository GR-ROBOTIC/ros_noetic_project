
#!/usr/bin/env python3
import sys, rospy, moveit_commander, math
from sensor_msgs.msg import JointState

def to_360(rad):
    deg = math.degrees(rad) % 360
    return deg if deg >= 0 else deg + 360

def callback(msg):
    print("\n--- Positions (0-360°) ---")
    for name, pos in zip(msg.name, msg.position):
        print(f"{name}: {to_360(pos):.2f}°")

def main():
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('robot_commander', anonymous=True)
    
    arm = moveit_commander.MoveGroupCommander("arm")
    rospy.Subscriber("/joint_states", JointState, callback)
    
    rospy.sleep(1)
    print("Envoi vers position cible...")
    
    # Cible : Waist 90°, Shoulder 45°, Elbow -30°, Wrist 0°
    target = [math.radians(90), math.radians(45), math.radians(-30), 0]
    arm.go(target, wait=True)
    arm.stop()
    
    rospy.spin()

if __name__ == '__main__':
    main()