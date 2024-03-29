#!/usr/bin/env python
# encoding: utf-8

"""
A Modified version of Hiwonder's `publish_point.py` for the `jethexa_navigation`
package. The goal is to support various orientations.
"""
import rospy
from move_base_msgs.msg import *
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import PoseStamped

goal_count = 0
goal_index = 0
try_again = True
add_more_point = False
markerArray = MarkerArray()

def status_callback(msg):
    global try_again, goal_index, add_more_point
    
    if msg.status.status == 3:
        try_again = True
        if not add_more_point: # one point finish
            print('No additional points to add.')
        if goal_index < goal_count:
            pose = PoseStamped()
            pose.header.frame_id = map_frame
            pose.header.stamp = rospy.Time.now()
            pose.pose.position.x = markerArray.markers[goal_index].pose.position.x
            pose.pose.position.y = markerArray.markers[goal_index].pose.position.y
            pose.pose.orientation.x = markerArray.markers[goal_index].pose.orientation.x
            pose.pose.orientation.y = markerArray.markers[goal_index].pose.orientation.y
            pose.pose.orientation.z = markerArray.markers[goal_index].pose.orientation.z
            pose.pose.orientation.w = markerArray.markers[goal_index].pose.orientation.w
            goal_pub.publish(pose)
            goal_index += 1
        elif goal_index == goal_count: # one point finish
            add_more_point = True
    else:
        print('Goal cannot reached has some error :', msg.status.status, ' try again!!!!')
        if try_again:
            pose = PoseStamped()
            pose.header.frame_id = map_frame
            pose.header.stamp = rospy.Time.now()
            pose.pose.position.x = markerArray.markers[goal_index - 1].pose.position.x
            pose.pose.position.y = markerArray.markers[goal_index - 1].pose.position.y
            pose.pose.orientation.x = markerArray.markers[goal_index - 1].pose.orientation.x
            pose.pose.orientation.y = markerArray.markers[goal_index - 1].pose.orientation.y
            pose.pose.orientation.z = markerArray.markers[goal_index - 1].pose.orientation.z
            pose.pose.orientation.w = markerArray.markers[goal_index - 1].pose.orientation.w
            goal_pub.publish(pose)
            try_again = False
        elif goal_index < len(markerArray.markers):
            pose = PoseStamped()
            pose.header.frame_id = map_frame
            pose.header.stamp = rospy.Time.now()
            pose.pose.position.x = markerArray.markers[goal_index].pose.position.x
            pose.pose.position.y = markerArray.markers[goal_index].pose.position.y
            pose.pose.orientation.x = markerArray.markers[goal_index].pose.orientation.x
            pose.pose.orientation.y = markerArray.markers[goal_index].pose.orientation.y
            pose.pose.orientation.z = markerArray.markers[goal_index].pose.orientation.z
            pose.pose.orientation.w = markerArray.markers[goal_index].pose.orientation.w
            goal_pub.publish(pose)
            goal_index += 1

def click_callback(msg):
    global goal_index, add_more_point
    global goal_count

    marker = Marker()
    marker.header.frame_id = map_frame
    marker.type = marker.TEXT_VIEW_FACING
    marker.action = marker.ADD
    marker.scale.x = 0.2
    marker.scale.y = 0.2
    marker.scale.z = 0.2
    marker.color.a = 1
    marker.color.r = 1
    marker.color.g = 0
    marker.color.b = 0
    #marker.lifetime = rospy.Duration(20)
    marker.pose.orientation.x = msg.pose.orientation.x
    marker.pose.orientation.y = msg.pose.orientation.y
    marker.pose.orientation.z = msg.pose.orientation.z
    marker.pose.orientation.w = msg.pose.orientation.w
    marker.pose.position.x = msg.pose.position.x
    marker.pose.position.y = msg.pose.position.y
    marker.pose.position.z = msg.pose.position.z
    marker.text = str(goal_count)
    
    markerArray.markers.append(marker)
    marker_id = 0
    for m in markerArray.markers:
        m.id = marker_id
        marker_id += 1
    mark_pub.publish(markerArray)

    if goal_count == 0:
        pose = PoseStamped()
        pose.header.frame_id = map_frame
        pose.header.stamp = rospy.Time.now()
        pose.pose.position.x = msg.pose.position.x
        pose.pose.position.y = msg.pose.position.y
        pose.pose.orientation.x = msg.pose.orientation.x
        pose.pose.orientation.y = msg.pose.orientation.y
        pose.pose.orientation.z = msg.pose.orientation.z
        pose.pose.orientation.w = msg.pose.orientation.w
        goal_pub.publish(pose)
        goal_index += 1
    elif add_more_point:
        add_more_point = False
        move = MoveBaseActionResult()
        move.status.status = 3
        move.header.stamp = rospy.Time.now()
        goal_status_pub.publish(move)
    
    goal_count += 1
    
    print('Added a goal point\n')

if __name__ == '__main__':
    rospy.init_node('publish_point_node')
   
    map_frame = rospy.get_param('~map_frame', 'map')
    clicked_point = rospy.get_param('~clicked_point', 'clicked_point')
    move_base_result = rospy.get_param('~move_base_result', 'move_base/result')
    
    mark_pub = rospy.Publisher('path_point', MarkerArray, queue_size=100)
    click_sub = rospy.Subscriber(clicked_point, PoseStamped, click_callback)
    
    goal_pub = rospy.Publisher('move_base_simple/goal', PoseStamped, queue_size=1)
    goal_status_sub = rospy.Subscriber(move_base_result, MoveBaseActionResult, status_callback)
    goal_status_pub = rospy.Publisher(move_base_result, MoveBaseActionResult, queue_size=1)
    
    rospy.spin()

