#!/usr/bin/env python

from wiimote.msg import State
from std_srvs.srv import Trigger
from dnb_remote_robot_control.srv import *
from sensor_msgs.msg import *

import rospy
import time

srv_heartbeat = None
srv_cartesian = None
srv_stop = None
srv_stop2 = None
#srv_io = None

state = None
current_base = "ur_base"
trans_or_rot = True

start_time = time.time()
last_message = time.time()

stopped_called = False
command_send = None

off = True



def callback(data):

	start_time = time.time()


	#print data 
	#return

	global state
	global current_base
	global trans_or_rot
	global last_message
	global stopped_called
	global off
	global command_send

	#print data


	if data.buttons[7] > 0.9: 

		if off:
			if current_base == "ur_base":
				print "stich to tool"
				current_base = "dnb_tool_frame"
			else:
				current_base = "ur_base"
			off = False

	if data.buttons[7] < 0.5:
		off = True

	#return


	command = StartMoveCartesianRequest()
	command.pose.move_delta = True
	command.pose.pose_reference = current_base
	command.speed = 1.0

	pressed = False

	if data.axes[0] < -0.3:
		command.pose.position.x = -data.axes[0] #  1.0
		pressed = True
	if data.axes[0] > 0.3:
		command.pose.position.x = -data.axes[0] #-1.0
		pressed = True
	if data.axes[1] < -0.3:
		command.pose.position.y = data.axes[1] #-1.0
		pressed = True
	if data.axes[1] > 0.3:
		command.pose.position.y = data.axes[1] #1.0
		pressed = True
	if data.axes[2] < -0.3:
		command.pose.position.z = data.axes[2]
		pressed = True
	if data.axes[5] < -0.3:
		command.pose.position.z = -data.axes[5]
		pressed = True


	if data.axes[3] < -0.3:
		command.pose.orientation.rx = -data.axes[3] #  1.0
		pressed = True
	if data.axes[3] > 0.3:
		command.pose.orientation.rx = -data.axes[3] #-1.0
		pressed = True
	if data.axes[4] < -0.3:
		command.pose.orientation.ry = data.axes[4] #-1.0
		pressed = True
	if data.axes[4] > 0.3:
		command.pose.orientation.ry = data.axes[4] #1.0
		pressed = True
	if data.buttons[4] > 0.9:
		command.pose.orientation.rz = -1.0
		pressed = True
	if data.buttons[5] > 0.9:
		command.pose.orientation.rz = 1.0
		pressed = True


	if pressed:
		command_send = command

		# Allow only 1 Hz
		#if time.time() - last_message > 1.0:

			#print "B1"
			#print data
			#print command
			#srv_cartesian(command)
			#stopped_called = False

			#last_message = time.time()

	else:
		command_send = None

		#if not stopped_called:
			#print "B2"
			#print "stop move"
			#srv_stop2()
			#srv_stop()
			#time.sleep(0.1)
			#stopped_called = True

	"""
	if time.time() - start_time < 1.0:
		print "A"
		if pressed:
			print "A1"
			return # allow 1 Hz max
		else:
			print "A2"
			print "stop move"
			srv_stop2()
			srv_stop()
	else:
		print "B"

		start_time = time.time()

		if pressed:
			print "B1"
			print data
			print command
			srv_cartesian(command)
		else:
			print "B2"
			print "stop move"
			srv_stop2()
			srv_stop()
	"""

	return 




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
	#srv_io = rospy.ServiceProxy("/set_io", SetIO)

	# In this case we need to call the heartbeat in loop, joy comes only after change in the pad
	sleeper = rospy.Rate(50)

	send_time = time.time()
	command_active = False

	while not rospy.is_shutdown():
		#if time.time() - start_time > 1.0:
		#	srv_stop2()
		#	srv_stop()
		#	start_time = time.time()


		# Send the command:
		if time.time() - send_time > 0.1:
			if command_send:
				srv_cartesian(command_send)
				command_active = True
			send_time = time.time()

		if not command_send:
			if command_active:
				srv_stop2()
				srv_stop()
				time.sleep(0.1)
				srv_stop2()
				srv_stop()
				command_active = False


		srv_heartbeat()
		sleeper.sleep()