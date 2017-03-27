import Leap
from SampleGiada import SampleListener
from tornado.ioloop import PeriodicCallback, IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.websocket import WebSocketHandler
import random
import queue

#This is intended to faciliate communication between Leap Motion and ROS
#The current data is only a placeholder
#It will be replaced by actual processed tracking info once implemented

class LeapWSHandler(WebSocketHandler):
	clients = [] #list of listening clients
	listener = SampleListener()
	controller = Leap.Controller()
	Q = queue.Queue()

	def check_origin(self, origin):
		return True

	def test(self):
		return self.send_data("x: " + str(random.random()*2))

	def getLeapData(self):
		# Keep this process running until Enter is pressed
		frame = LeapWSHandler.controller.frame()
		hands = frame.hands
		s = ""

		for hand in frame.hands:
			handType = "Left hand" if hand.is_left else "Right hand"

			print("  %s, id %d, position: %s" % (
				handType, hand.id, hand.palm_position))

			# Get the hand's normal vector and direction
			normal    = hand.palm_normal
			direction = hand.direction

			# Calculate the hand's pitch, roll, and yaw angles
			s += ("  pitch: %f degrees, roll: %f degrees, yaw: %f degrees\n" % (
				direction.pitch * Leap.RAD_TO_DEG,
				normal.roll     * Leap.RAD_TO_DEG,
				direction.yaw   * Leap.RAD_TO_DEG))

			# Get arm bone
			arm = hand.arm
			s += ("  Arm direction: %s, wrist position: %s, elbow position: %s\n" % (
				arm.direction,
				arm.wrist_position,
				arm.elbow_position))

		return self.send_data(s)

	def open(self):
		# Have the sample listener receive events from the controller
		LeapWSHandler.controller.add_listener(LeapWSHandler.listener)
		LeapWSHandler.clients.append(self)
		self.callback = PeriodicCallback(self.getLeapData, 500)
		self.callback.start()

	def on_message(self, message):
		print(message)

	def on_close(self):
		# Remove the sample listener when done
		LeapWSHandler.controller.remove_listener(LeapWSHandler.listener)
		
		LeapWSHandler.clients.remove(self)
		self.callback.stop()

	@classmethod
	def send_data(l, data):
		for client in l.clients:
			try:
				client.write_message(data)
			except:
				print("Fail to send data to client.")

def main():
	#tornado.ioloop.IOLoop.instance().stop()
	app = Application([
		(r"/ws", LeapWSHandler),
	])

	hs = HTTPServer(app)
	hs.listen(8888)
	IOLoop.instance().start()

main()
