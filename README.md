# Baxter-Teleoperation
Teleoperation of Baxter using Leap Motion
TODO: Code for Kinect motion tracking

## DEPENDENCIES
* Python 3.4 (https://www.python.org/downloads/release/python-343/)
* Tornado 4.4.3 (http://www.tornadoweb.org/en/stable/)
* Leap Motion SDK (user/operator side) (https://developer.leapmotion.com/)
* ROS (client/Baxter side) (http://wiki.ros.org/ROS/Installation)

## TEST INSTRUCTION
Edit the line 
```
hs.listen(8888, address="------")
```
of `WebSocketTest.py` so the address parameter contains the IP address of the server computer. If server and client code runs on the same machine, you may make the line simply be
```
hs.listen(8888)
```
. 

Similarly, edit the lat line of `rosside.py`, specifically
```
client = Client("ws://127.0.0.1:8888/ws", 5)
```
so it contains the IP address of the server computer if it is different from the one running client code. Specifically, replace `127.0.0.1` with the IP address and leave everything else the same. Otherwise, no edit is necessary. If you want to monitor incoming data with a better interface, open `webtest.html`, enter the IP address of the server in the `host` field, and click "open".

Run `WebSocketTest.py` first on the server computer and then `rosside.py` and/or `webtest.html` on the client side. Data should be streaming in terminal and/or webpage.

## NOTE
`WebSocketTest.py` contains code for the server (Leap Motion) side to read from Leap Motion and perform preliminary conversion between the coordinate systems.

`rosside.py` contains code for the client (ROS/Baxter) side to process data from the current frame and translate it to control Baxter.

`webtest.html` contains code for monitoring purpose.

`vr.html` contains code for streaming webcam videos into VR headset.

## PROGRESS UPDATE
* **03/26** Completed integration of Leap Motion with Server
* **04/09** Tentative data translation from Leap Motion to ROS
* **04/14** Completed preliminary integration of Leap Motion and Baxter
* **04/20** Tested gesture mapping on a small scale
* **04/24** Working demo. Need to improve precision and eliminate noise.
