#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from flask import Flask, request

# Initialize the Flask app
app = Flask(__name__)
ros_publisher = None

# This route listens for HTTP POST requests at the /print_done URL
@app.route('/print_done', methods=['POST'])
def handle_print_done():
    rospy.loginfo("SUCCESS: Webhook received from Raspberry Pi!")
    
    # Publish a message to the ROS network
    if ros_publisher:
        ros_publisher.publish("PRINT_COMPLETE_START_KINOVA")
        rospy.loginfo("Published trigger to /octoprint/status topic.")
        
    return "Webhook processed by ROS", 200

def main():
    global ros_publisher
    
    # Initialize the ROS node
    rospy.init_node('octoprint_webhook_listener', anonymous=True)
    
    # Create a publisher on the topic '/octoprint/status'
    ros_publisher = rospy.Publisher('/octoprint/status', String, queue_size=10)
    
    rospy.loginfo("ROS Listener Node is active.")
    rospy.loginfo("Starting Flask server. Waiting for OctoPrint...")
    
    # Run the Flask server. 
    # host='0.0.0.0' explicitly allows external connections (from the Pi)
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()