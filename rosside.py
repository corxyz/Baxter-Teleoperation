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
#from threading import Thread
#import base_geom as base_geom

#ROS side data request
#position info in the most recent frame of Leap

pos = {"L":[-.056424434661865234,0.08955266571044922, 0.1807218780517578, \
            0.0, 0.0, 0.0, 1.0], 
       "R":[-0.07449254608154297, -0.1174264907836914, 0.19524444580078125, \
            0.0, 0.0, 0.0, 1.0]} 
#position info in the most recent frame of Baxterb


bpos = {"L":[0.4795606784002749, 0.568933407474859, 0.18754802195350023, \
             0.05045439425577075, 0.7321941859790739, -0.05684833045624352, \
             0.6768414108512136], 
        "R":[0.44889235508456976, -0.6404624981274808, 0.19186524586206288, \
            -0.09562397715077178, 0.7314424103831731, 0.0018074254860270165, \
            0.6751627866669149]
        }

client = None
is_running = True

justonce = 0

class Client(object):
    def __init__(self, url, timeout, t):
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        self.dl = copy.copy(pos["L"]) #default left hand position
        self.dr = copy.copy(pos["R"]) #default right hand position
        self.t = t
        self.bdl = copy.copy(bpos["L"])
        self.bdr = copy.copy(bpos["R"])
        self.gpos_l = 0.0855
        self.gpos_r = 0.037
        #self.moveToDefault()
        global pos, bpos, is_running
        print bpos
        is_running = True
        PeriodicCallback(self.tryAgain, 5000, io_loop=self.ioloop).start()
        print 'callback started\n'
        self.ioloop.start()
    
    def moveToDefault(self):
        print "Moved to default:"
        x = list(self.t.robot.FK(arm=LEFT)) 
        xc = x[0] - self.bdl[0]
        yc = x[1] - self.bdl[1]
        zc = x[2] - self.bdl[2]
        dt = max(abs(xc/0.05), abs(yc/0.05), abs(zc/0.05))
        dx = xc/dt
        dy = yc/dt
        dz = zc/dt
        x_traj = [None] * (int(dt+2))
        x_traj[0] = x
        for i in range(1, int(dt+2)):
          x_traj[i] = [x[0] - dx * i, x[1] - dy * i, x[2] - dz * i] + x[3:]
        if (x_traj[-1] == None): x_traj = x_traj[:-1]
        if (x_traj[-1] == None): x_traj = x_traj[:-1]

        c = x_traj
        te = [(i+1) *2.0 for i in range(len(c))]
        print 'FollowXTraj',c, te
        self.t.robot.FollowXTraj(c, te, x_ext = None, arm=LEFT, blocking=False)       
        
        x = list(self.t.robot.FK(arm=RIGHT)) 
        xc = x[0] - self.bdr[0]
        yc = x[1] - self.bdr[1]
        zc = x[2] - self.bdr[2]
        dt = max(abs(xc/0.05), abs(yc/0.05), abs(zc/0.05))
        dx = xc/dt
        dy = yc/dt
        dz = zc/dt
        x_traj = [None] * (int(dt+2))
        x_traj[0] = x
        for i in range(1, int(dt+1)):
          x_traj[i] = [x[0] - dx * i, x[1] - dy * i, x[2] - dz * i] + x[3:]
        if (x_traj[-1] == None): x_traj = x_traj[:-1]

        c = x_traj
        te = [i *2.0 for i in range(len(c))]
        self.t.robot.FollowXTraj(c, te, x_ext = None, arm=RIGHT, blocking=False)

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

    def parseLeapLeft(self, l):
        global pos
        #get absolute 3-d coordinates
        if (len(l) > 2): 
            a = l[2][1:-1].split(",")
            for i in range(len(a)): 
                if (i == 0): a[i] = float(a[i].encode("ascii")[1:-1]) / 1000.0
                else: a[i] = float(a[i].encode("ascii")[2:-1]) / 1000.0
            pos["L"] = copy.copy(a)
        else: pos["L"] = [0.0, 0.0, 0.0]
        #absolute Euler angles
        if (len(l) > 5): 
            lang = [float(l[4].encode("ascii")), float(l[3].encode("ascii")), \
                    float(l[5].encode("ascii"))]
        else: lang = [0.0, 0.0, 0.0]
        #transform Euler angles into Quaternion
        lquat = numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(
            lang[0], lang[1], lang[2]))
        pos["L"] += lquat
        #update parameters to control gripper
        if (len(l) > 6):
          pinch_strength = float(l[6].encode("ascii"))
          self.gpos_l = 0.0855 - pinch_strength*0.0855

    def parseLeapRight(self, r):
        global pos
        #get absolute 3-d coordinates
        if (len(r) > 2): 
            a = r[2][1:-1].split(",")
            for i in range(len(a)): 
                if (i == 0): a[i] = float(a[i].encode("ascii")[1:-1]) / 1000.0
                else: a[i] = float(a[i].encode("ascii")[2:-1]) / 1000.0
            pos["R"] = copy.copy(a)
        else: 
            pos["R"] = [0.0, 0.0, 0.0]        
        #absolute Euler angles
        if (len(r) > 5): 
            rang = [float(r[4].encode("ascii")), float(r[3].encode("ascii")), \
                    float(r[5].encode("ascii"))]
        else: rang = [0.0, 0.0, 0.0]
        #transform Euler angles into Quaternion
        rquat = numpy.ndarray.tolist(tf.transformations.quaternion_from_euler(
            rang[0], rang[1], rang[2]))
        pos["R"] += rquat
        #update parameters to control gripper
        if (len(r) > 6):
          pinch_strength = float(r[6].encode("ascii"))
          self.gpos_r = 0.037 - pinch_strength*0.037
        
    def scaleToBaxter(self,delta):
        newx = delta[0]
        newy = delta[1]
        newz = delta[2]
        bdelta = [newx, newy, newz]
        bdelta += delta[3:]
        return bdelta

    def parseLeapData(self, msg):
        global pos
        a = list(map(lambda x: x.split("^"), msg.splitlines()))
        l = r = []
        lang = rang = []
        if (a[0][0].startswith("Left")): l = a[0]
        else: r = a[0]
        if (len(a) > 1 and a[1][0].startswith("Right")): r = a[1]
        elif (len(a) > 1): l = a[1]
        print l, r
        #get absolute 3-d coordinates
        self.parseLeapLeft(l)
        self.parseLeapRight(r)
        
    def renewDefault(self):
        global pos
        self.dl = pos["L"]
        self.dr = pos["R"]
     
    def leap_to_baxter(self):
        global pos, bpos
        bdl = self.bdl
        bdr = self.bdr
          
        current_l = pos["L"]
        default_l = self.dl
        delta_l = TransformRightInv(current_l, default_l) #type: list

        current_r = pos["R"]
        default_r = self.dr
        delta_r = TransformRightInv(current_r, default_r) #type: list

        #scale delta_human to delta_baxter
        bdelta_l = self.scaleToBaxter(delta_l)
        bdelta_r = self.scaleToBaxter(delta_r)
        self.t.viz.test.AddCube(current_r, [0.2,0.1,0.3], 
            rgb=self.t.viz.test.ICol(0), alpha=0.5, mid=2)
        
        #calculate rotation angles in delta_baxter
        bdelta_l = bdelta_l[:3] + RotToQ(Rodrigues(0.1*InvRodrigues(QToRot(
            bdelta_l[3:])))).tolist()
        bdelta_r = bdelta_r[:3] + RotToQ(Rodrigues(0.1*InvRodrigues(QToRot(
            bdelta_r[3:])))).tolist()
        
        baxter_l = Transform(bdelta_l, bdl)
        baxter_r = Transform(bdelta_r, bdr)
        
        bpos["L"] = baxter_l
        bpos["R"] = baxter_r

    def solveIK(self):
        global bpos
        print "Trying to solve IK..."
        ql = self.t.robot.IK(bpos["L"], arm=LEFT)
        qr = self.t.robot.IK(bpos["R"], arm=RIGHT)
        print 'IK solution= {q1} {q2}'.format(q1=ql, q2=qr)
        if ql is not None:
            dqth= 0.1
            ql0= self.t.robot.Q(arm=LEFT)
            dqmax= max([abs(q1-q0) for q1,q0 in zip(ql,ql0)])
            if dqmax>dqth:  ql= [q0+(q1-q0)*dqth/dqmax for q1,q0 in zip(ql,ql0)]
        if qr is not None:
            dqth= 0.1
            qr0= self.t.robot.Q(arm=RIGHT)
            dqmax= max([abs(q1-q0) for q1,q0 in zip(qr,qr0)])
            if dqmax>dqth:  qr= [q0+(q1-q0)*dqth/dqmax for q1,q0 in zip(qr,qr0)]
        return (ql, qr) 

    def moveBaxter(self, ql, qr):
        if ql != None: self.t.robot.MoveToQ(ql, dt=0.01, arm=LEFT)
        if qr != None: self.t.robot.MoveToQ(qr, dt=0.01, arm=RIGHT)
    
    def moveGripper(self):
        self.t.robot.MoveGripper(self.gpos_l, arm=LEFT)
        self.t.robot.MoveGripper(self.gpos_r, arm=RIGHT)
    
    @gen.coroutine
    def run(self):
        global pos, bpos, is_running
        #c = 0
        self.t.kbhit.Activate()
        try:
            while True:
                if self.t.kbhit.IsActive():
                    key= self.t.kbhit.KBHit()
                    if key=='q':
                        is_running = False
                        break;
                else:
                    break
                #read message on websocket server
                msg = yield self.ws.read_message()
                if msg is None:
                    print("Connection closed.")
                    self.ws = None
                    break
                #process message
                elif(msg != ""):
                    #c += 1
                    print msg
                    self.parseLeapData(msg)
                    self.leap_to_baxter()
                    print "*******************************************"
                    print pos
                    print bpos
                    self.t.viz.test.AddCube(bpos["L"], [0.2,0.1,0.3], 
                        rgb=self.t.viz.test.ICol(2), alpha=0.5, mid=0)
                    self.t.viz.test.AddCube(bpos["R"], [0.2,0.1,0.3], 
                        rgb=self.t.viz.test.ICol(2), alpha=0.5, mid=1)
                    (ql, qr) = self.solveIK()
                    self.moveBaxter(ql, qr)
                    self.moveGripper()
                else:
                    print 'no msg'
        finally:
            self.t.kbhit.Deactivate()

    def tryAgain(self):
        global is_running
        if self.ws is None:
            print("Lost connection. Trying to reconnect now...")
            self.connect()
        elif not is_running:
            print "Stopped.\n"
            self.ioloop.stop()
            self.ioloop.close()
            self.ioloop.clear_instance()

def initClient(t):
    global client, pos
    if (client == None):
        client = Client("ws://128.237.136.61:8888/ws", 5, t)
        print "Teleoperation system closed.\n"

def Run(t,*args):
    global bpos, count
    print "Running..."
    t.viz.test= TSimpleVisualizer(name_space='visualizer_test')
    t.viz.test.viz_frame= t.robot.BaseFrame
    initClient(t)
