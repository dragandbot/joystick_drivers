#!/usr/bin/env python

from wiimote.msg import State
from std_srvs.srv import Trigger
from dnb_remote_robot_control.srv import *
import zimmer_grippers.srv
from sensor_msgs.msg import *
from robot_movement_interface.srv import *

import rospy
import time

srv_heartbeat = None
srv_cartesian = None
srv_stop = None
srv_stop2 = None
srv_io = None

state = None
current_base = "dnb_tool_frame"

is_opened = True

#!/usr/bin/env python

def open_zimmer():
	global is_opened
	port = 1
	detectworkpiece = False
	timeout = float(2)
	direction = 1
	# Message response returns 1 if base / work position arrived, 2 if teach position, -1 if timeout, -2 if undef pose, -3 other errors
	move_gripper_srv = rospy.ServiceProxy('/zimmer_grippers/move_gripper', zimmer_grippers.srv.MoveGripper)
	resp = move_gripper_srv(port, direction, detectworkpiece, timeout) 
	is_opened = True

def close_zimmer():
	global is_opened
	port = 1
	detectworkpiece = False
	timeout = float(2)
	direction = 2
	# Message response returns 1 if base / work position arrived, 2 if teach position, -1 if timeout, -2 if undef pose, -3 other errors
	move_gripper_srv = rospy.ServiceProxy('/zimmer_grippers/move_gripper', zimmer_grippers.srv.MoveGripper)
	resp = move_gripper_srv(port, direction, detectworkpiece, timeout) 
	is_opened = False


def callback(data):

	global state
	global is_opened
	global current_base

	print data.buttons
	srv_heartbeat()

	if data.buttons[0]: 
		current_base = "dnb_tool_frame"
	if data.buttons[1]:
		current_base = "ur_base"

	command = StartMoveCartesianRequest()
	command.pose.move_delta = True
	command.pose.pose_reference = current_base
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
		elif data.buttons[10]:
			if is_opened:
				srv_io(3, True)
				is_opened = False
				#close_zimmer()
			else:
				srv_io(3, False)
				is_opened = True
				#open_zimmer()
		else:
			time.sleep(0.1)
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
		elif data.buttons[10]:
			if is_opened:
				srv_io(3, True)
				is_opened = False
				#close_zimmer()
			else:
				srv_io(3, False)
				is_opened = True
				#open_zimmer()
		else:
			time.sleep(0.1)
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
	srv_io = rospy.ServiceProxy("/set_io", SetIO)

	rospy.spin()