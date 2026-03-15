cmake_minimum_required(VERSION 3.0.2)
project(kinova_tending)

# Find the standard ROS build tools
find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  geometry_msgs
)

catkin_package()

# Tell ROS where your Python executable scripts live
# This ensures rosrun can find them!
catkin_install_python(PROGRAMS
  scripts/kinova_print_tender.py
  scripts/octoprint_listener.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
