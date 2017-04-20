#modified from https://github.com/ilkerkesen/tornado-websocket-client-example/blob/master/client.py

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
# import ROS
import json
from core_tool import *
import defaultpos as dp
reload(dp)
import tf
import numpy
import copy
from threading import Thread
#import base_geom as base_geom

#ROS side data request
pos = {"L":[.2, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0], "R":[-.2, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]}  #position info in the most recent frame of Leap
bpos = {"L":[.2, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0], "R":[-.2, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]} #position info in the most recent frame of Baxter
pbpos = copy.copy(bpos)
client = None

class Client(object):
    def __init__(self, url, timeout, t):
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        self.dl = dp.DefaultPos() #default left hand position
        self.dr = dp.DefaultPos("R") #default right hand position
        #self.bdl = dp.BaxterDefaultPos() #Baxter default left hand position
        #self.bdr = dp.BaxterDefaultPos("R") #Baxter default right hand position
        self.bdl = t.robot.FK(arm=LEFT)
        self.bdr = t.robot.FK(arm=RIGHT)
        self.t = t
        global pos, bpos
        #pos["L"] = pos["R"] = bpos["L"] = bpos["R"] = []
        print bpos
        PeriodicCallback(self.tryAgain, 20000, io_loop=self.ioloop).start()
        print 'callback started\n'
        self.ioloop.start()
        print 'init finish\n'

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
        global pos, bpos, pbpos
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
        #bdefault_l = [self.bdl.x, self.bdl.y, self.bdl.z]
        #bdefault_l += numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(self.bdl.roll, self.bdl.pitch, self.bdl.yaw))
        
        baxter_l = Transform(bdelta_l, self.bdl)
        

        #bdefault_r = [self.bdr.x, self.bdr.y, self.bdr.z]
        #bdefault_r += numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(self.bdr.roll, self.bdr.pitch, self.bdr.yaw))
        baxter_r = Transform(bdelta_r, self.bdr)
        print bdelta_l, bdelta_r
        print baxter_l, baxter_r

        #update Baxter position to move to (pos_baxter)
	pbpos = copy.copy(bpos)
        bpos["L"] = baxter_l
        bpos["R"] = baxter_r


    @gen.coroutine
    def run(self):
        global pos, bpos
        c = 0
        while True:
            c += 1
            print "aaa"
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
                #pos["L"].append(lang)
                #pos["R"].append(rang)
                #transform Euler angles into Quaternion
                lquat = numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(lang[0], lang[1], lang[2]))
                rquat = numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(rang[0], rang[1], rang[2]))
                pos["L"] += lquat
                pos["R"] += rquat
                self.leap_to_baxter()
                print "************"
                print bpos
		ql = self.t.robot.IK(bpos["L"], arm=LEFT)
		print "in move..."
		qr = self.t.robot.IK(bpos["R"], arm=RIGHT)
		print 'IK solution= {q1} {q2}'.format(q1=ql, q2=qr)
            else:
	        print 'no msg'


    def tryAgain(self):
        if self.ws is None:
            print("Lost connection. Trying to reconnect now...")
            self.connect()

def bpos_is_changed():
    global bpos, pbpos
    if (bpos["L"] != pbpos["L"]): return True
    elif (bpos["R"] != pbpos["R"]): return True
    else: return False

def initClient(t):
    global client
    print "initClient"
    if (client == None):
	client = Client("ws://128.237.182.62:8888/ws", 5, t)
	print "client initlized.\n"
    
"""
def move(t):
    global pos, bpos, count
    print "trying to move (really hard)..."
    print pos, bpos
    while bpos:
      ql = t.robot.IK(bpos["L"], arm=LEFT)
      print "in move..."
      qr = t.robot.IK(bpos["R"], arm=RIGHT)
      print 'IK solution= {q1} {q2}'.format(q1=ql, q2=qr)
    return True
    """

def Run(t):
    global bpos, count
    print "Running..."
    initClient(t)
    #B = Thread(target=move, args=(t,))
    #def f ():
    #  B.run()
    #A.start() 
    #t = threading.Timer(5.0, f)
    #t.start()
    #ql = t.robot.IK(bpos["L"], arm="LEFT")
    #qr = t.robot.IK(bpos["R"], arm="RIGHT")
    #print 'IK solution= {q}'.format(q=q)

def Run(t, *args):
        #global pos, bpos, pbpos
        #calculate delta_human
        if len(args) >= 2:
	  bdl = t.robot.FK(arm=LEFT)
	  bdr = t.robot.FK(arm=RIGHT)
	  
	  current_l = args[0]
	  default_l = [0.0, 0.03, 0.0175]
	  default_l += numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(0.0, 0.0, 0.0))
	  delta_l = TransformRightInv(current_l, default_l) #type: list

	  current_r = args[1]
	  default_r = [0.0, -0.03, 0.0175]
	  default_r += numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(0.0, 0.0, 0.0))
	  delta_r = TransformRightInv(current_r, default_r) #type: list
	  
	  deltaQ_l = delta_l[3:]
	  deltaQ_r = delta_r[3:]
	  
	  print delta_l
	  print delta_r
	  print "Baxter: "

        #scale delta_human to delta_baxter
	  bdelta_l = dp.BaxterDefaultPos.scaleToBaxter(delta_l)
	  bdelta_r = dp.BaxterDefaultPos.scaleToBaxter(delta_r)
	  
	  bdelta_l = bdelta_l[:3] + RotToQ(Rodrigues(0.1*InvRodrigues(QToRot(bdelta_l[3:])))).tolist()
	  bdelta_r = bdelta_r[:3] + RotToQ(Rodrigues(0.1*InvRodrigues(QToRot(bdelta_r[3:])))).tolist()

        #calculate delta_baxter
        #not sure if the order of arguments to base_geom.Transform is correct
        #bdefault_l = [self.bdl.x, self.bdl.y, self.bdl.z]
        #bdefault_l += numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(self.bdl.roll, self.bdl.pitch, self.bdl.yaw))
        
	  baxter_l = Transform(bdelta_l, bdl)
        

        #bdefault_r = [self.bdr.x, self.bdr.y, self.bdr.z]
        #bdefault_r += numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(self.bdr.roll, self.bdr.pitch, self.bdr.yaw))
	  baxter_r = Transform(bdelta_r, bdr)
	  print bdelta_l, bdelta_r
	  print baxter_l, baxter_r
	  
	  print "*****************"
	  ql = t.robot.IK(baxter_l, arm=LEFT)
	  qr = t.robot.IK(baxter_r, arm=RIGHT)
	  print 'IK solution= {q1} {q2}'.format(q1=ql, q2=qr)
        #update Baxter position to move to (pos_baxter)
	#pbpos = copy.copy(bpos)
        #bpos["L"] = baxter_l
        #bpos["R"] = baxter_r
    
    # def moveArm(*args):
    #     arm= args[0]
    #     dp= args[1]
    #     x= list(t.robot.FK(arm=arm))  #Current end-effector pose
    #     x_trg= [x[d]+dp[d] for d in range(3)] + x[3:]  #Target
    #     print 'Moving {arm}-arm to {x}'.format(arm=LRToStr(arm), x=x_trg)
    #     t.robot.MoveToX(x_trg, dt=4.0, arm=arm)
'''
    while(len(pos) != 0):

        if(pos[0] != "Right hand"):
            println("RIGHT HAND: "  + d) #?
            # moveArm("RIGHT", d['Right hand'])
        if(pos[0] != "Left hand"):
            println("LEFT: "  + d)
            # moveArm("LEFT", d['Left hand'])
            from core_tool import *
            '''