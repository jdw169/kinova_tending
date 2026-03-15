
Markdown
# Kinova Gen3-Lite 3D Print Tending Workcell

A complete, dynamic ROS Noetic package that bridges a physical 3D printer with a simulated Kinova Gen3-Lite robotic arm. This project creates an automated, pick-and-place pipeline: when a print finishes on a CR-10S, OctoPrint triggers a MoveIt trajectory to safely extract the finished part.

## 🏗️ System Architecture

This project spans across three distinct layers (Embedded, Network, and Physics):

1. **The Slicer / Firmware:** Use Ultmaker slicer. Flash Klipper firmware to the CR-10S 3D printer motherboard and install Klipper on a Raspberry Pi 4B connected to the printer through USB.
2. **The Webhook Bridge:** OctoPrint even manager executes a local bash script (`trigger_ros.sh`) when a print is finished. A string "print_done" is sent using HTTP POST.
3. **The ROS Execution:** A Flask server (`octoprint_listener.py`) receives the HTTP data and publishes it to a ROS topic. The MoveIt trajectory planner (`kinova_print_tender.py`) catches the trigger, generates a Cartesian path (avoiding the injected CR-10S bed/gantry collision boxes), and commands the Gazebo simulation to execute the pick-and-place sequence.

## ⚙️ Prerequisites

* **OS:** Ubuntu 20.04
* **ROS Version:** ROS 1 Noetic
* **Robot Packages:** Official `ros-kortex` (Kinova) driver and MoveIt packages.
* **3D Printer:** OctoPrint installed (Raspberry Pi recommended) alongside Klipper firmware

## 📥 Installation

**1. Clone the repository into your catkin workspace:**
bash
cd ~/catkin_ws/src
git clone https://github.com/jdw169/kinova_tending
2. Make the Python scripts executable:

Bash
cd ~/catkin_ws/src/kinova_tending/scripts
chmod +x kinova_print_tender.py octoprint_listener.py
3. Build the workspace:

Bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
**2. 🛠️ Hardware Setup (OctoPrint & Klipper)**
To connect your physical printer to the ROS simulation, configure the following:

Klipper:
Download the Klipper firmware from Klipper official repository and flash the 3D printer MCU. Install Klipper main firmware on a Linux computer, Raspberry Pi recommended. 

OctoPrint:
Download and install Octoprint on the same Linux computer. Recommend using the Raspberry Pi Imager to create OctoPi image on the SD card and run it on a Raspberry Pi. 
Setup Octoprint to connect to Klipper firmware through virtual serial port. Refer to Klipper official documentation. 
Add event trigger in Octoprint event manager. Open Octoprint setting in web interface. Click Event Manager tab and add event. Select print_done event and add system command "~/trigger_ros.sh". Put the "trigger_ros.sh" in your home directory or any directory but remeber to update the path of the command in Octoprint Event Manager.

**3. 🚀 Usage**
To launch the full print-tending simulation pipeline, you will need three terminals:

Terminal 1: Launch the Kinova Gazebo Simulation
(Use your standard Kortex Gazebo launch file for the Gen3 Lite)

```Bash
roslaunch kortex_gazebo spawn_kortex_robot.launch robot:=gen3_lite
Terminal 2: Start the Flask Webhook Server

```Bash
rosrun kinova_tending octoprint_listener.py
Terminal 3: Start the MoveIt Print Tender Node
(Note: Must be launched inside the robot's namespace)

```Bash
rosrun kinova_tending kinova_print_tender.py __ns:=my_gen3_lite
Once all nodes are active and report "Ready", trigger a print finish via OctoPrint (or manually via rostopic pub) to watch the automated pick-and-place sequence!

📂 Repository Structure
scripts/ - Core Python ROS nodes (Flask server and MoveIt planner).

config/ - RViz configuration files (tending_setup.rviz).

extras/ - Bash scripts and configuration snippets for the OctoPrint/Raspberry Pi setup.

📜 License
MIT License
