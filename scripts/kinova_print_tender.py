#!/usr/bin/env python3
import sys
import rospy
import moveit_commander
import geometry_msgs.msg
from std_msgs.msg import String
from moveit_commander.conversions import pose_to_list
import copy

class KinovaPrintTender:
    def __init__(self):
        # Initialize the moveit_commander and ROS node
        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node('kinova_print_tender', anonymous=True)

        # Instantiate MoveIt objects
        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()
        self.move_group = moveit_commander.MoveGroupCommander("arm")

        # Set move group
        self.move_group = moveit_commander.MoveGroupCommander("arm")
        self.gripper_group = moveit_commander.MoveGroupCommander("gripper")
        # Give the scene a second to initialize before adding objects
        rospy.sleep(2) 
        self.build_printer_collision_zones()

        # Subscribe to the OctoPrint trigger topic
        rospy.Subscriber('/octoprint/status', String, self.trigger_callback)
        rospy.loginfo("Kinova Node Ready. Waiting for PrintDone trigger...")

    def build_printer_collision_zones(self):
        rospy.loginfo("Building CR-10S collision zones...")
        
        # Add the Print Bed (A flat box below the arm's target area)
        bed_pose = geometry_msgs.msg.PoseStamped()
        bed_pose.header.frame_id = self.robot.get_planning_frame()
        bed_pose.pose.position.x = 0.5   # Distance in front of the robot
        bed_pose.pose.position.y = 0.0
        bed_pose.pose.position.z = 0.1   # Height of the bed
        self.scene.add_box("printer_bed", bed_pose, size=(0.3, 0.3, 0.05))

        # Add the Gantry (A vertical wall behind the bed)
        gantry_pose = geometry_msgs.msg.PoseStamped()
        gantry_pose.header.frame_id = self.robot.get_planning_frame()
        gantry_pose.pose.position.x = 0.65 
        gantry_pose.pose.position.y = 0.0
        gantry_pose.pose.position.z = 0.3
        self.scene.add_box("printer_gantry", gantry_pose, size=(0.05, 0.4, 0.4))

    def trigger_callback(self, msg):
        if msg.data == "PRINT_COMPLETE_START_KINOVA":
            rospy.loginfo("Trigger received! Initiating part removal trajectory...")
            self.pick_and_place()

    def operate_gripper(self, state):
        # Get the active motorized joint
        motorized_joint = self.gripper_group.get_active_joints()[0]
        
        # Use dictionary to code clamp open/close
        target_dict = {}
        if state == "opened":
            target_dict[motorized_joint] = 0.96
        elif state == "closed":
            target_dict[motorized_joint] = 0.0
            
        rospy.loginfo(f"Commanding {motorized_joint} to: {target_dict[motorized_joint]}")
        
        # Execute using the dictionary target
        self.gripper_group.set_joint_value_target(target_dict)
        success = self.gripper_group.go(wait=True)
        
        # Stop any residual joint commands
        self.gripper_group.stop() 
        
        if success:
            rospy.loginfo("Gripper command sent to physics engine successfully.")
        else:
            rospy.logwarn("MoveIt failed to execute gripper command.")
            
        rospy.sleep(1) # Give the physics engine a second to settle

    def pick_and_place(self):
        rospy.loginfo("Starting Pick-and-Place sequence...")
        standby_pose = self.move_group.get_current_pose().pose

        # Ensure gripper is open before approaching
        self.operate_gripper("opened")

        # Hover directly over the center of the print bed
        target_pose = copy.deepcopy(standby_pose)
        target_pose.position.x = 0.50
        target_pose.position.y = 0.0
        target_pose.position.z = 0.30 # Safe hovering height
        
        rospy.loginfo("Moving to hover position...")
        self.move_group.set_pose_target(target_pose)
        self.move_group.go(wait=True)

        # Dip down to grab the printed part
        target_pose.position.z = 0.15 # Lower down toward the bed
        rospy.loginfo("Dipping to grasp height...")
        self.move_group.set_pose_target(target_pose)
        self.move_group.go(wait=True)

        # Close the gripper
        self.operate_gripper("closed")

        # Lift the part back up
        target_pose.position.z = 0.25
        rospy.loginfo("Lifting part...")
        self.move_group.set_pose_target(target_pose)
        self.move_group.go(wait=True)

        # Move to the drop-off zone
        target_pose.position.x = 0.25
        target_pose.position.y = 0.20
        rospy.loginfo("Moving to drop-off zone...")
        self.move_group.set_pose_target(target_pose)
        self.move_group.go(wait=True)

        # Open gripper to drop the part
        self.operate_gripper("opened")

        # Return to the Standby Position
        rospy.loginfo("Returning to standby position...")
        self.move_group.set_pose_target(standby_pose)
        self.move_group.go(wait=True)
        
        rospy.loginfo("Pick-and-Place complete! Waiting for next print...")

if __name__ == '__main__':
    try:
        KinovaPrintTender()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
