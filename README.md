# Baxter-Teleoperation
Code for remote data communication between Leap Motion and ROS (websocket)
TODO: Code for Kinect motion tracking

## DEPENDENCIES
* Python 2.7
* Tornado
* Leap Motion SDK

## TEST INSTRUCTION
Run `WebSocketTest.py` first and `rosside.py` and/or `webtest.html`. Data should be streaming in terminal and/or webpage.

## NOTE
`WebSocketTest.py` contains code for the server (Leap Motion) side.
`rosside.py` contains code for the client (ROS/Baxter) side.
`webtest.html` contains code for monitoring purpose.
