Step-by-Step
Open your terminal:

Bash
nano ~/catkin_ws/src/kinova_tending/README.md
Paste the following text:

Markdown
# Kinova Gen3-Lite 3D Print Tending Workcell

A complete, dynamic ROS Noetic package that bridges a physical 3D printer with a simulated Kinova Gen3-Lite robotic arm. This project creates an automated, context-aware pick-and-place pipeline: when a print finishes on a CR-10S, OctoPrint triggers a MoveIt trajectory to safely extract the finished part using dynamically calculated collision geometries.

## 🏗️ System Architecture

This project spans across three distinct layers (Embedded, Network, and Physics):

1. **The Slicer / Firmware:** Custom end G-code (`OCTO99`) contains the exact X, Y, and Z dimensions of the printed part. Klipper firmware is configured to safely bypass this macro.
2. **The Webhook Bridge:** OctoPrint (via the GCODE System Commands plugin) catches the `OCTO99` command and executes a local bash script (`trigger_ros.sh`). This script packages the dimensions into a JSON payload and POSTs it across the local network.
3. **The ROS Execution:** A Flask server (`octoprint_listener.py`) receives the HTTP payload and publishes it to a ROS topic. The MoveIt trajectory planner (`kinova_print_tender.py`) catches the trigger, generates a dynamic Cartesian path (avoiding the injected CR-10S bed/gantry collision boxes), and commands the Gazebo simulation to execute the pick-and-place sequence.

## ⚙️ Prerequisites

* **OS:** Ubuntu 20.04
* **ROS Version:** ROS 1 Noetic
* **Robot Packages:** Official `ros-kortex` (Kinova) driver and MoveIt packages.
* **3D Printer:** OctoPrint installed (Raspberry Pi recommended) with the "GCODE System Commands" plugin.

## 📥 Installation

**1. Clone the repository into your catkin workspace:**
```bash
cd ~/catkin_ws/src
git clone <YOUR_GITHUB_REPO_URL> kinova_tending
2. Make the Python scripts executable:

Bash
cd ~/catkin_ws/src/kinova_tending/scripts
chmod +x kinova_print_tender.py octoprint_listener.py
3. Build the workspace:

Bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
🛠️ Hardware Setup (OctoPrint & Klipper)
To connect your physical printer to the ROS simulation, configure the following:

Klipper:
Add a dummy macro to your printer.cfg so the firmware does not halt on the custom trigger:

Plaintext
[gcode_macro OCTO99]
gcode:
    # ROS trigger bypass
OctoPrint:

Install the GCODE System Commands plugin.

Add a new command triggered by OCTO99 that points to the provided bash script: /path/to/trigger_ros.sh %(1)s %(2)s %(3)s

Update trigger_ros.sh (found in the /extras folder) with the IP address of your Ubuntu ROS machine.

🚀 Usage
To launch the full print-tending simulation pipeline, you will need three terminals:

Terminal 1: Launch the Kinova Gazebo Simulation
(Use your standard Kortex Gazebo launch file for the Gen3 Lite)

Bash
roslaunch kortex_gazebo spawn_kortex_robot.launch robot:=gen3_lite
Terminal 2: Start the Flask Webhook Server

Bash
rosrun kinova_tending octoprint_listener.py
Terminal 3: Start the MoveIt Print Tender Node
(Note: Must be launched inside the robot's namespace)

Bash
rosrun kinova_tending kinova_print_tender.py __ns:=my_gen3_lite
Once all nodes are active and report "Ready", trigger a print finish via OctoPrint (or manually via rostopic pub) to watch the automated pick-and-place sequence!

📂 Repository Structure
scripts/ - Core Python ROS nodes (Flask server and MoveIt planner).

config/ - RViz configuration files (tending_setup.rviz).

extras/ - Bash scripts and configuration snippets for the OctoPrint/Raspberry Pi setup.

📜 License
MIT License
