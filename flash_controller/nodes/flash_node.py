#!/usr/bin/env python3
import os.path as op
from threading import Thread, Event
import time

import numpy as np

import rospy

from geometry_msgs.msg      import Twist
from std_msgs.msg           import Float32, Int16MultiArray, Int16, String
from sensor_msgs.msg        import Image

from flash_behaviors.msg    import Speech

from flash_controller.flash import Flash

fp 	= op.realpath(__file__)
fp 	= op.split(op.split(fp)[0])[0]
fp	= op.join(fp, 'src', 'urbi')


class FlashNode:
    """ ROS Node to control the flash robot. """

        
    PUBLISHER_RATE  = 30
    EMOTIONS        = ['Happy', 'Surprise', 'Angry', 'Fear', 'Disgust', 'Sad', 'Yawn']

    
    def __init__(self):
        """ Initializes the FLASH ROS node. """
        self.name = self.__class__.__name__
        rospy.init_node(self.name)

        self.sub_cmd_vel   = rospy.Subscriber('/flash_robot/cmd_vel',     Twist,     self.cmdVelCallback)
        self.sub_behave    = rospy.Subscriber('/flash_robot/behave',      Int16,     self.behaveCallback)
        self.sub_speech    = rospy.Subscriber('/flash_robot/say',         Speech,    self.speechCallback)
        self.sub_emotion   = rospy.Subscriber('/flash_robot/emotion',     String,    self.emotionCallback)


        # startup FLASH
        self.flash         = Flash()

        self.cmd_vel_ts    = time.time()
        self.cmd_vel_flag  = False

        # load expressions        
        with open(op.join(fp, 'expressions.u'), 'r') as f:
            self.flash.uw.send(f.read())

        # load controls
        with open(op.join(fp, 'gamepad_control.u'), 'r') as f:
            print(self.flash.uw.send(f.read()))


    def speechCallback(self, msg):
        self.flash.say(msg.text, msg.intensity)

    
    def cmdVelCallback(self, msg):
        self.cmd_vel_ts   = time.time()
        self.cmd_vel_flag = True
        cmd               = "robot.body.x.speed = %i & robot.body.yaw.speed = %i" % (200.*msg.linear.x, 20.*msg.angular.z)
        self.flash.uw.send(cmd)
        print('cmd_vel', cmd)


    def behaveCallback(self, msg):

	# Button Back
        if msg.data == 6:
            self.flash.say('Hello. My name is Alyx. Nice to meet you. Welcome to the HRI Laboratory.')
            self.flash.say('You might have noticed that I have a very expressive face.')
            self.flash.say('I can get angry.')
            self.flash.exp('Angry')
            self.flash.say('I can show disgust.')
            self.flash.exp('Disgust')
            self.flash.say('Also, I can be sad.')
            self.flash.exp('Sad')
            self.flash.say('or be surprised.')
            self.flash.exp('Surprise')
            self.flash.say('and sometimes I am afraid')
            self.flash.exp('Fear')
            self.flash.say('If I am bored I can get very sleepy')
            self.flash.exp('Yawn')

        # Button A
        elif msg.data == 0:
            print(self.flash.uw.send('robot.control.button_a()'))

        # Button B
        elif msg.data == 1:
            self.flash.uw.send('robot.control.button_b()')

        # Button X
        elif msg.data == 2:
            self.flash.uw.send('robot.control.button_x()')

        # Button Y
        elif msg.data == 3:
            print(self.flash.uw.send('robot.control.button_y()'))

        # Button RB
        elif msg.data == 5:
            self.flash.uw.send('robot.control.button_rb()')

        # Button Start
        elif msg.data == 7:
            print(self.flash.uw.send('robot.control.button_start()'))


    def emotionCallback(self, msg):
        if msg.data and msg.data in self.EMOTIONS:
            self.flash.exp(msg.data)


    def update(self):
        
        if self.cmd_vel_flag and (self.cmd_vel_ts - time.time()) > 0.1:
            self.flash.uw.send("robot.body.x.speed = 0 & robot.body.yaw.speed = 0")
            self.cmd_vel_flag = False
            print ("Robot stopped")


if __name__ == '__main__':
    ros_node  = FlashNode()
    ros_rate  = rospy.Rate(ros_node.PUBLISHER_RATE)

    try:
        rospy.loginfo(ros_node.name + " started")
        while not rospy.is_shutdown():
            ros_node.update()
            ros_rate.sleep()

    except rospy.ROSInterruptException as exception:
        print (exception)
