#modified from https://github.com/ilkerkesen/tornado-websocket-client-example/blob/master/client.py

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
# import ROS
import json
# from core_tool import *

#ROS side data request
pos = list();

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
        except Exception as e:
            # print()
            print("Connection error: " + str(e))
        else:
            print("Connected.")
            self.run()

    @gen.coroutine
    def run(self):
        c = 0
        while True:
            c += 1
            #read message on websocket server
            msg = yield self.ws.read_message()
            if msg is None:
                print("Connection closed.")
                self.ws = None
                break
            #process message
            if(msg != ""):
                f = msg.split("^")
                spos = f[2];
                pos = list(map(float, spos[1:-1].split(",")))


    def tryAgain(self):
        if self.ws is None:
            print("Lost connection. Trying to reconnect now...")
            self.connect()


def Run(t):
    # def moveArm(*args):
    #     arm= args[0]
    #     dp= args[1]
    #     x= list(t.robot.FK(arm=arm))  #Current end-effector pose
    #     x_trg= [x[d]+dp[d] for d in range(3)] + x[3:]  #Target
    #     print 'Moving {arm}-arm to {x}'.format(arm=LRToStr(arm), x=x_trg)
    #     t.robot.MoveToX(x_trg, dt=4.0, arm=arm)


    while(len(pos) != 0):
        if(pos[0] != "Right hand"):
            println("RIGHT HAND: "  + d)
            # moveArm("RIGHT", d['Right hand'])
        if(pos[0] != "Left hand"):
            println("LEFT: "  + d)
            # moveArm("LEFT", d['Left hand'])

if __name__ == "__main__":
    client = Client("ws://128.237.212.54:8888/ws", 5)





