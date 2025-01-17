#! /usr/bin/env python

import rospy

import actionlib

from flash_controller.flash import Flash
from flash_behaviors.msg import BehaveAction

class BehaveActionServer(object):
    
    def __init__(self, name):
        
        # Robot controller.
        self.flash = Flash()

        # Action server.
        self._action_name = name
        self._as = actionlib.SimpleActionServer(self._action_name, BehaveAction, execute_cb=self.execute_cb, auto_start = False)
        self._as.start()

        rospy.loginfo("Behavior action server started!")

      
    def execute_cb(self, goal):
        
        behavior = goal.behavior
        duration = goal.duration
        intensity = goal.intensity

        # Add validation of requested behavior...

        if duration:
            if intensity:
                self.flash.exp(behavior, duration, intensity)
            else:
                self.flash.exp(behavior, duration)
        else:
            self.flash.exp(behavior)
          
        self._as.set_succeeded()
        

if __name__ == '__main__':
    
    rospy.init_node('behavior_server')
    server = BehaveActionServer(rospy.get_name())
    rospy.spin()