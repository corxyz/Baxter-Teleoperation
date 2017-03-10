import Leap
import tornado.ioloop
import tornado.options
import tornado.websocket
import tornado.web
import tornado.httpserver
import websocket
import json
import random

class TListener(Leap.Listener):

	def on_init(self, controller):
		print "Listener initialized."

	def on_connect(self, controller):
		print "Listener connected."

	def on_frame(self, controller):
		pass

	def on_images(self, controller):
		pass

	def on_device_change(self, controller):
		pass

	def on_device_failure(self, controller):
		pass

	def on_diagnostic_event(self, controller):
		pass

	def on_disconnect(self, controller):
		print "Listener disonnected."

	def on_exit(self, controller):
		pass

class LeapWSHandler(tornado.websocket.WebSocketHandler):
	clients = set()

	def check_origin(self, origin):
		return True

	def test(self):
		return self.write_message("x: " + str(random.random()*2))

	def open(self):
		LeapWSHandler.clients.add(self)
		self.callback = tornado.ioloop.PeriodicCallback(self.test, 1000)
		self.callback.start()

	def on_message(self, message):
		print message

	def on_close(self):
		LeapWSHandler.clients.remove(self)
		self.callback.stop()

	@classmethod
	def send_data(l, data):
		for client in l.clients:
			try:
				client.write_message(data)
			except:
				print "Fail to send data to server."

def test():
	counter = random.randint(0,11)
	return counter

def main():
	#tornado.ioloop.IOLoop.instance().stop()
	app = tornado.web.Application([
		(r"/ws", LeapWSHandler),
	])

	hs = tornado.httpserver.HTTPServer(app)
	hs.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
"""
def main():
    logging.basicConfig(level=logging.INFO)
    tornado.options.define("port", default=8888, help="run on the given port", type=int)
    tornado.options.define("playback", default=None, help="A frame data recording file (in json format) to playback isntead of getting data from the Leap", type=str)
    tornado.options.define("playbackDelay", default=5.0, help="How long to wait (in seconds) before playing back the recording (only relevant when using --playback)", type=float)
    tornado.options.define("loop", default=False, help="Whether to loop playback of the recording (only relevant when using --playback)", type=bool)
    tornado.options.define("record", default=None, help="The name of a file to record frame data to.  Can be played back with --playback=<file name>", type=str)
    tornado.options.define("recordingDelay", default=5.0, help="How long to wait (in seconds) before starting to record (only relevant when using --record)", type=float)

    tornado.options.parse_command_line()
    app = Application(tornado.options.options)
    app.listen(tornado.options.options.port)
    print "%s listening on http://%s:%s" % (__file__, "0.0.0.0", tornado.options.options.port)
    print "ctrl-c to stop!"
    tornado.ioloop.IOLoop.instance().start()
"""
main()