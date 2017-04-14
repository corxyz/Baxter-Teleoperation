#modified from https://github.com/ilkerkesen/tornado-websocket-client-example/blob/master/client.py

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
import json
from core_tool import *
import defaultpos as dp
import tf
import numpy
import copy

#ROS side data request
pos = dict() #position info in the most recent frame of Leap
bpos = dict() #position info in the most recent frame of Baxter
client = None

class Client(object):
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        self.dl = dp.DefaultPos() #default left hand position
        self.dr = dp.DefaultPos("R") #default right hand position
        self.bdl = dp.BaxterDefaultPos() #Baxter default left hand position
        self.bdr = dp.BaxterDefaultPos("R") #Baxter default right hand position
        global pos, bpos
        pos["L"] = pos["R"] = bpos["L"] = bpos["R"] = []
        PeriodicCallback(self.tryAgain, 20000, io_loop=self.ioloop).start()
        self.ioloop.start()

    @gen.coroutine
    def connect(self):
        print("Connecting...")
        try:
            #client connect to websocket server
            self.ws = yield websocket_connect(self.url)
        except Exception as e:
            print("Connection error: " + str(e))
        else:
            print("Connected.")
            self.run()

    def leap_to_baxter(self):
        global pos, bpos
        #calculate delta_human
        current_l = pos["L"]
        default_l = [self.dl.x, self.dl.y, self.dl.z]
        default_l += numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(self.dl.roll, self.dl.pitch, self.dl.yaw))

        delta_l = TransformRightInv(current_l, default_l) #type: list
        current_r = pos["R"]
        default_r = [self.dr.x, self.dr.y, self.dr.z]
        default_r += numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(self.dr.roll, self.dr.pitch, self.dr.yaw))

        delta_r = TransformRightInv(current_r, default_r) #type: list

        #scale delta_human to delta_baxter
        bdelta_l = dp.BaxterDefaultPos.scaleToBaxter(delta_l)
        bdelta_r = dp.BaxterDefaultPos.scaleToBaxter(delta_r)

        #calculate delta_baxter
        #not sure if the order of arguments to base_geom.Transform is correct
        bdefault_l = [self.bdl.x, self.bdl.y, self.bdl.z]
        bdefault_l += numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(self.bdl.roll, self.bdl.pitch, self.bdl.yaw))
        baxter_l = Transform(bdefault_l, bdelta_l)

        bdefault_r = [self.bdr.x, self.bdr.y, self.bdr.z]
        bdefault_r += numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(self.bdr.roll, self.bdr.pitch, self.bdr.yaw))
        baxter_r = Transform(bdefault_r, bdelta_r)

        #update Baxter position to move to (pos_baxter)
        bpos["L"] = baxter_l
        bpos["R"] = baxter_r

    @gen.coroutine
    def run(self):
        global pos
        c = 0 #for debugging
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
                print msg
                a = list(map(lambda x: x.split("^"), msg.splitlines()))
                l = r = []
                lang = rang = []
                if (a[0][0].startswith("Left")): l = a[0]
                else: r = a[0]
                if (len(a) > 1 and a[1][0].startswith("Right")): r = a[1]
                elif (len(a) > 1): l = a[1]
                #get absolute 3-d coordinates
                if (len(l) > 2):
                  a = l[2][1:-1].split(",")
                  for i in range(len(a)):
                    if (i == 0): a[i] = float(a[i].encode("ascii")[1:-1])
                    else: a[i] = float(a[i].encode("ascii")[2:-1])
                  pos["L"] = copy.copy(a)
                else: pos["L"] = [0.0, 0.0, 0.0]
                if (len(r) > 2):
                  a = r[2][1:-1].split(",")
                  for i in range(len(a)):
                    if (i == 0): a[i] = float(a[i].encode("ascii")[1:-1])
                    else: a[i] = float(a[i].encode("ascii")[2:-1])
                  pos["R"] = copy.copy(a)
                else: pos["R"] = [0.0, 0.0, 0.0]

                #absolute Euler angles
                if (len(l) > 5): lang = [float(l[4].encode("ascii")), float(l[3].encode("ascii")), float(l[5].encode("ascii"))]
                else: lang = [0.0, 0.0, 0.0]
                if (len(r) > 5): rang = [float(r[4].encode("ascii")), float(r[3].encode("ascii")), float(r[5].encode("ascii"))]
                else: rang = [0.0, 0.0, 0.0]

                #transform Euler angles into Quaternion
                lquat = numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(lang[0], lang[1], lang[2]))
                rquat = numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(rang[0], rang[1], rang[2]))
                pos["L"] += lquat
                pos["R"] += rquat
                self.leap_to_baxter()
            else:
                print 'no msg'

    def tryAgain(self):
        if self.ws is None:
            print("Lost connection. Trying to reconnect now...")
            self.connect()

def initClient():
    global client
    if (client == None):
        client = Client("ws://128.237.174.225:8888/ws", 5)
        print "client initlized.\n"

def Run(t, *args):
    initClient()
    global bpos
    ql = t.robot.IK(bpos["L"], arm="LEFT")
    qr = t.robot.IK(bpos["R"], arm="RIGHT")
    print 'IK solution= {q}'.format(q=q)
    # def moveArm(*args):
    #     arm= args[0]
    #     dp= args[1]
    #     x= list(t.robot.FK(arm=arm))  #Current end-effector pose
    #     x_trg= [x[d]+dp[d] for d in range(3)] + x[3:]  #Target
    #     print 'Moving {arm}-arm to {x}'.format(arm=LRToStr(arm), x=x_trg)
    #     t.robot.MoveToX(x_trg, dt=4.0, arm=arm)
