#!/usr/bin/env python

import cv2
import rospy
import cv_bridge
import sensor_msgs.msg


BRIDGE  = cv_bridge.CvBridge()
URI     = 'http://10.0.0.195:8081/video.mjpg'


def main():
    rospy.init_node('CameraNode')

    cam = cv2.VideoCapture(URI)
    pub = rospy.Publisher('/flash_robot/camera', sensor_msgs.msg.Image, queue_size = 1)
    
    # Shutdown hook
    rospy.on_shutdown(cam.release)

    rospy.loginfo("CameraNode started")
    
    # keep going till shutdown
    while cam.isOpened() and not rospy.is_shutdown():
        ret, frame = cam.read()
        if ret:
            pub.publish(BRIDGE.cv2_to_imgmsg(frame, encoding = "bgr8"))


if __name__ == '__main__':
    main()
