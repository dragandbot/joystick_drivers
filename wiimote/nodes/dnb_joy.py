#!/usr/bin/env python

from wiimote.msg import State
from std_srvs.srv import Trigger
from dnb_remote_robot_control.srv import *
from sensor_msgs.msg import *

import rospy

srv_heartbeat = None
srv_cartesian = None
srv_stop = None
srv_stop2 = None

state = None
current_base = "dnb_tool_frame"
trans_or_rot = True

def callback(data):

	global state
	global current_base
	global trans_or_rot

	#print data

	if data.buttons[0]: 
		current_base = "dnb_tool_frame"
	if data.buttons[1]:
		current_base = "base_link"

	command = StartMoveCartesianRequest()
	command.pose.move_delta = True
	command.pose.pose_reference = current_base
	command.speed = 1.0

	if state and data.axes == state.axes and data.buttons == state.buttons:
		return
	else:
		state = data

	if data.buttons[8]:
		print "mode changed translation <-> rotation"
		trans_or_rot = not trans_or_rot

	print state.axes
	print state.buttons

	if not trans_or_rot:

		if data.axes[1] > 0.1:
			print "-y"
			command.pose.orientation.ry = 1.0
		elif data.axes[1] < -0.1:
			print "+y"
			command.pose.orientation.ry = -1.0
		elif data.axes[0] > 0.1:
			print "-x"
			command.pose.orientation.rx = -1.0
		elif data.axes[0] < -0.1:
			print "+x"
			command.pose.orientation.rx = 1.0
		elif data.buttons[6] > 0.1:
			print "-z"
			command.pose.orientation.rz = -1.0
		elif data.buttons[7] > 0.1:
			print "+z"
			command.pose.orientation.rz = 1.0
		else:
			print "stop move"
			srv_stop2()
			srv_stop()

	else:

		if data.axes[1] > 0.1:
			print "-y"
			command.pose.position.y = 1.0
		elif data.axes[1] < -0.1:
			print "+y"
			command.pose.position.y = -1.0
		elif data.axes[0] > 0.1:
			print "-x"
			command.pose.position.x = -1.0
		elif data.axes[0] < -0.1:
			print "+x"
			command.pose.position.x = 1.0
		elif data.buttons[6] > 0.1:
			print "-z"
			command.pose.position.z = -1.0
		elif data.buttons[7] > 0.1:
			print "+z"
			command.pose.position.z = 1.0
		else:
			print "stop move"
			srv_stop2()
			srv_stop()


	srv_cartesian(command)

if __name__ == '__main__':
	rospy.init_node("dnb_wiimote")
	rospy.Subscriber("/joy", Joy, callback)

	srv_heartbeat = rospy.ServiceProxy("/dnb_remote_robot_control/heartbeat", Trigger)
	srv_cartesian = rospy.ServiceProxy("/remotecontrol_start_move_cartesian", StartMoveCartesian)
	srv_stop = rospy.ServiceProxy("/remotecontrol_stop_move", Trigger)
	srv_stop2 = rospy.ServiceProxy("/stop_robot_right_now", Trigger)

	# In this case we need to call the heartbeat in loop, joy comes only after change in the pad
	sleeper = rospy.Rate(50)
	while not rospy.is_shutdown():
		srv_heartbeat()
		sleeper.sleep()