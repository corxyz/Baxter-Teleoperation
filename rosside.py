#modified from https://github.com/ilkerkesen/tornado-websocket-client-example/blob/master/client.py

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect

#ROS side data request

class Client(object):
	def __init__(self, url, timeout):
		self.url = url
		self.timeout = timeout
		self.ioloop = IOLoop.instance()
		self.ws = None
		self.connect()
		PeriodicCallback(self.tryAgain, 20000, io_loop=self.ioloop).start()
		self.ioloop.start()

	@gen.coroutine
	def connect(self):
		print("Connecting...")
		try:
			#client connect to websocket server
			self.ws = yield websocket_connect(self.url)
		except (Exception, e):
			print("Connection error: " + str(e))
		else:
			print("Connected.")
			self.run()

	@gen.coroutine
	def run(self):
		while True:
			#read message on websocket server
			msg = yield self.ws.read_message()
			if msg is None:
				print("Connection closed.")
				self.ws = None
				break

			print(msg)

	def tryAgain(self):
		if self.ws is None:
			print("Lost connection. Trying to reconnect now...")
			self.connect()

if __name__ == "__main__":
	client = Client("ws://localhost:8888/ws", 5)
