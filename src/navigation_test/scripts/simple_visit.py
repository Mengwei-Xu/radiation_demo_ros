#!/usr/bin/env python

# a simple visit

import sys
import getpass
current_user = getpass.getuser()
pointlib_path = "/home/{0}/catkin_ws/shared_python".format(current_user)
sys.path.insert(0,pointlib_path)
from Point import CPoint
from Point import LOCATIONS
# from https://hotblackrobotics.github.io/en/blog/2018/01/29/seq-goals-py/

import rospy
import math

import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
from geometry_msgs.msg import Pose, Point, Quaternion
from tf.transformations import quaternion_from_euler


class SimpleVisit():

    def __init__(self):

        self.current_goal_pose = None
        self.goal_list = None
        self.goal_locations = None
        self.locations_reached = []
        self.current_goal = None
        self.goal_number = -1
        
        rospy.init_node('simple_visit')
        self.client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        rospy.loginfo("Waiting for move_base action server...")
        wait = self.client.wait_for_server(rospy.Duration(5.0))
        if not wait:
            rospy.logerr("Action server not available!")
            rospy.signal_shutdown("Action server not available!")
            return

        rospy.loginfo("Connected to move base server")


    def active_callback(self):
        rospy.loginfo("Processing "+str(self.current_goal_pose))


    def feedback_callback(self,feedback):
        #rospy.loginfo("Feedback for "+str(self.current_goal_pose)+":"+str(feedback))
        #rospy.loginfo("Feedback received for "+str(self.current_goal_pose))
        pass

    def create_goal(self,current_goal_pose):
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = current_goal_pose.x
        goal.target_pose.pose.position.y = current_goal_pose.y
        goal.target_pose.pose.position.z = current_goal_pose.z
        goal.target_pose.pose.orientation.w = 1.0
        return goal

    def send_next_goal(self):
        result = False
        
        if len(self.goal_list) > 0:
            self.goal_number = self.goal_number + 1
            self.current_goal = self.goal_locations[self.goal_number]
            
            self.current_goal_pose = self.goal_list.pop(0)
            goal = self.create_goal(self.current_goal_pose)
            self.client.send_goal(goal,self.done_callback,self.active_callback,self.feedback_callback)
            result = True

        rospy.loginfo("Goals executed")
        rospy.loginfo(self.locations_reached)
        
        return result
        
        

    def done_callback(self,status,result):
        if status == GoalStatus.PREEMPTED:
            rospy.loginfo("Goal "+str(self.current_goal_pose)+" received a cancel request after it started execution")
            
        elif status == GoalStatus.SUCCEEDED:
            rospy.loginfo("Goal "+str(self.current_goal_pose)+" reached")
            self.locations_reached.append(self.current_goal)
            if not self.send_next_goal():
                rospy.loginfo("Visited all locations")
                rospy.signal_shutdown("Shutting down simple visit")
                return 

        elif status == GoalStatus.ABORTED:
            rospy.loginfo("Goal "+str(self.current_goal_pose)+" aborted")
            rospy.signal_shutdown("Shutting down simple visit")
            return 

        elif status == GoalStatus.REJECTED:
            rospy.loginfo("Goal "+str(self.current_goal_pose)+" rejected")
            rospy.signal_shutdown("Shutting down simple visit")
            return 

        elif status == GoalStatus.RECALLED:
            rospy.loginfo("Goal "+str(self.current_goal_pose)+" received a cancel request before execution. Cancelled!")

            
    def start(self,locs):
        
        
        self.goal_locations = locs
        self.goal_list = []
        for loc in locs:
            self.goal_list.append(LOCATIONS[loc])

        rospy.loginfo("Prepared goals list")
        rospy.loginfo(self.goal_list)


        self.send_next_goal()

        rospy.spin()


if __name__ == '__main__':

    try:
        locs = ['entrance','bigtankfront','tank1top','pipes']
        simple_visit = SimpleVisit()
        simple_visit.start(locs)

    except rospy.ROSInterruptException:
        rospy.loginfo("Node shutdown")
        
        
        

        

        
            


        


            
            
            
                
                
                
            
