#!/usr/bin/env python

""" operator.py 
 Node for operator controls.
 Gives Bebop Status updates such as battery state 
 Gives control for the control state of the Bebop: Manual or Follow
 Manual: Provides manual telemetry control over the Bebop.
    - run key_cam.py, key_op.py, and cmd_pub.py in the bebop_app package.
 Follow: Follows an Apriltag
    - run continuous_detection.launch from the apriltags2_ros package along with follow.launch from the bebop_follow package. """

import rospy
import key_utilities as ku

#SENDIG COMMANDS TO BEBOP
from geometry_msgs.msg import Twist #Piloting, Camera
from std_msgs.msg import String #GPS Navigation Flight plans
from std_msgs.msg import Empty #Takeoff, Landing, Emergency, Pause/stop flight plan, Flat Trim, Snapshot
from std_msgs.msg import Bool #Navigate Home, toggle in flight video recording
from std_msgs.msg import UInt8 # Flight Animations
from std_msgs.msg import Float32 #camera exposure

#READING FROM BEBOP
#from sensor_msgs.msg import Image #Camera
from nav_msgs.msg import Odometry #Odometry
#from sensor_msgs.msg import NavStatFix #GPS
from sensor_msgs.msg import JointState #pan/tilt of the virtual camera
from bebop_msgs.msg import CommonCommonStateBatteryStateChanged as BatteryState
from bebop_msgs.msg import CommonCommonStateWifiSignalChanged as WifiSignal
#from bebop_msgs.msg import CommonCommonStateSensorsStatesListChanged as SensorsStatesList
from bebop_msgs.msg import CommonOverHeatStateOverHeatChanged as OverHeatState
from bebop_msgs.msg import CommonOverHeatStateOverHeatRegulationChanged as OverHeatRegulation
from bebop_msgs.msg import CommonCalibrationStateMagnetoCalibrationStateChanged as MagnetoCalibration
from bebop_msgs.msg import CommonCalibrationStateMagnetoCalibrationRequiredState as MagnetoCalibrationRequired
#from bebop_msgs.msg import CommonCalibrationStateMagnetoCalibrationAxisToCalibrateChanged as MagnetoCalibrationAxis
#from bebop_msgs.msg import CommonCalibrationStateMagnetoCalibrationStartedChanged as MagnetoCalibrationProcess
#from bebop_msgs.msg import CommonCalibrationStatePitotCalibrationStateChanged as PitotCalibrationState
#from bebop_msgs.msg import CommonHeadlightsStateintensityChanged as HeadlightsStateintensity #TODO: check if this applies to Bebop2

class operator_command():
   
    #Initializing all of the parameters
    def __init__(self):
        # Initializing Messages
	self.emptymsg = Empty()
        # Initializing Publications
        self.takeoff = rospy.Publisher("bebop/takeoff", Empty, queue_size = 1) #Note this assumes a bebop namespace. When flying more than one bebop, need to change this.
        self.land = rospy.Publisher("bebop/land", Empty, queue_size = 1)
        self.emergency = rospy.Publisher("bebop/reset", Empty, queue_size = 1)

        # Initializing Subscriptions TODO Move this to the appropriate spot. If Operator command is soley for operator input then there should be another node for output. See if we can also make this a graphical interface.
        self.odom = rospy.Subscriber("bebop/odom", Odometry, self.odom_update)
        self.camera_angle = rospy.Subscriber("bebop/joint_states", JointState, self.camera_angle_update)
        self.battery = rospy.Subscriber("bebop/states/common/CommonState/BatteryStateChanged", BatteryState, self.battery_update)
        self.wifi = rospy.Subscriber("bebop/states/common/CommonState/WifiSignalChanged", WifiSignal, self.wifi_update)
#        self.sensors = rospy.Subscriber("bebop/states/common/CommonState/SensorsStatesListChanged", SensorsStatesList, sensor_update)
        self.overheat = rospy.Subscriber("bebop/states/common/OverHeatState/OverHeatChanged", OverHeatState, self.overheat_update)
        self.overheatregulation = rospy.Subscriber("bebop/states/common/OverHeatState/OverHeatRegulationChanged", OverHeatRegulation, self.overheat_regulation_update)

    def odom_update(self, data):
        rospy.loginfo(rospy.get_caller_id() + " Odometry Update ")
        rospy.loginfo(data.twist.covariance)

    def camera_angle_update(self, data):
        rospy.loginfo(rospy.get_caller_id() + " Camera Angle Update:")
        rospy.loginfo("Pan: %0.1f", data.position[0])
        rospy.loginfo("Tilt: %0.1f", data.position[1])

    def battery_update(self, data):
        rospy.loginfo(rospy.get_caller_id() + " Battery Update %d\%", data.percent) 

    def wifi_update(self, data):
        rospy.loginfo(rospy.get_caller_id() + " Wifi Update %d dbm", data.rssi)

#    def sensor_update(self, data):
#        rospy.loginfo(rospy.get_caller_id() + " Sensor Update: %d IMU

    def overheat_update(self, data):
        rospy.logwarn(rospy.get_caller_id() + " WARNING: OVERHEAT TEMPERATURE REACHED")

    def overheat_regulation_update(self, data):
        if data.regulationType == 0:
            rospy.loginfo(rospy.get_caller_id() + "Over Heat Regulation: Ventilation")
        elif data.regulationType == 1:
            rospy.loginfo(rospy.get_caller_id() + "Over Heat Regulation: Switch Off")
        else:
            rospy.loginfo(rospy.get_caller_id() + "Over Heat Regulation: Unknown.")
            rospy.logbug(rospy.get_caller_id() + "Unknown Over Heat Regulation Change")
            rospy.logbug(data)
 
    def send(self):
	#Receiving key commands
        getch = ku._Getch()
        rate = rospy.Rate(50)
        # Initializing Variables
        manual = True
        grounded = True

        while not rospy.is_shutdown():
            key = getch()
	    #Running through all possibilities and publishing the appropriate commands.

            #Switch modes b/w Manual and Follow
            if key == "m":
                if manual == True:
                    rospy.loginfo("The mode is already Manual")
                    #TODO launch key_cmd.launch

                else:
                    manual = True
                    rospy.loginfo("Entering Manual mode")
            elif key == "f":
                if manual == False:
                    rospy.loginfo("The mode is already Follow")
                else:
                    manual = False
                    rospy.loginfo("Entering Follow mode")
            #Take Off
            elif key == ",":
                if grounded == True:
                    self.takeoff.publish(self.emptymsg)
                    grounded = False
                    rospy.loginfo("Taking off")
                else:
                    rospy.loginfo("Already in the air")

            #Landing
            elif key == ".":
                if grounded == False:
                    self.land.publish(self.emptymsg)
                    grounded = True
                    rospy.loginfo("Landing")
                else:
                    rospy.loginfo("Already Grounded")
            elif key == "z":
                rospy.loginfo("Shutdown initiated")
                rospy.signal_shutdown("Shutting down initiated by key_emergency_switch")
            else:
	        pass

            rate.sleep() #TODO: Check if this is run in parallel or nah. And so why is there two rate.sleeps one inoperator() and one in send().

#Below initializes the node, prints the commands associated with the function, and then sends the code to the "send" sub-function

def operator():
    rospy.init_node("operator_command")
    rate = rospy.Rate(1) #Rate in Hz
    kc = operator_command()
    print("Press 'm' to switch to manual mode.\n")
    print("Press 'f' to switch to follow mode.\n")
    print("Press ',' to take off.\n")
    print("Press '.' to land.\n")
    print("Press 'z' to terminate.\n")

    while not rospy.is_shutdown():
        kc.send()
        rate.sleep()

if __name__=="__main__":
    try:
        operator()
    finally:
        pass
