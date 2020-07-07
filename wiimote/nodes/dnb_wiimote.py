#!/usr/bin/env python

from wiimote.msg import State
from std_srvs.srv import Trigger
from dnb_remote_robot_control.srv import *

import rospy

srv_heartbeat = None
srv_cartesian = None
srv_stop = None
srv_stop2 = None

state = None

def callback(data):

	global state

	print data.buttons
	srv_heartbeat()

	command = StartMoveCartesianRequest()
	command.pose.move_delta = True
	command.pose.pose_reference = "dnb_tool_frame"
	command.speed = 1.0

	if state and data.buttons == state:
		return
	else:
		state = data.buttons

	if data.buttons[5]:

		if data.buttons[6]:
			command.pose.orientation.ry = 1.0
		elif data.buttons[7]:
			command.pose.orientation.ry = -1.0
		elif data.buttons[8]:
			command.pose.orientation.rx = -1.0
		elif data.buttons[9]:
			command.pose.orientation.rx = 1.0
		elif data.buttons[3]:
			command.pose.orientation.rz = -1.0
		elif data.buttons[2]:
			command.pose.orientation.rz = 1.0
		else:
			srv_stop2()
			srv_stop()

	else:

		if data.buttons[6]:
			command.pose.position.y = 1.0
		elif data.buttons[7]:
			command.pose.position.y = -1.0
		elif data.buttons[8]:
			command.pose.position.x = -1.0
		elif data.buttons[9]:
			command.pose.position.x = 1.0
		elif data.buttons[3]:
			command.pose.position.z = -1.0
		elif data.buttons[2]:
			command.pose.position.z = 1.0
		else:
			srv_stop2()
			srv_stop()

	srv_cartesian(command)










if __name__ == '__main__':
	rospy.init_node("dnb_wiimote")
	rospy.Subscriber("/wiimote/state", State, callback)

	srv_heartbeat = rospy.ServiceProxy("/dnb_remote_robot_control/heartbeat", Trigger)
	srv_cartesian = rospy.ServiceProxy("/remotecontrol_start_move_cartesian", StartMoveCartesian)
	srv_stop = rospy.ServiceProxy("/remotecontrol_stop_move", Trigger)
	srv_stop2 = rospy.ServiceProxy("/stop_robot_right_now", Trigger)

	rospy.spin()