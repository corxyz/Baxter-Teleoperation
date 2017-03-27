# Baxter-Teleoperation
Code for remote data communication between Leap Motion and ROS (websocket)
TODO: Code for Kinect motion tracking

## DEPENDENCIES
* Python 3.4
* Tornado
* Leap Motion SDK

## TEST INSTRUCTION
Run `WebSocketTest.py` first and `rosside.py` and/or `webtest.html`. Data should be streaming in terminal and/or webpage.

## NOTE
`WebSocketTest.py` contains code for the server (Leap Motion) side.

`rosside.py` contains code for the client (ROS/Baxter) side.

`webtest.html` contains code for monitoring purpose.

`vr.html` contains code for streaming webcam videos into VR headset.

## PROGRESS UPDATE
* **03/26** Completed integration of Leap Motion with Server
