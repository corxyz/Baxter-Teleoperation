#modified from https://github.com/ilkerkesen/tornado-websocket-client-example/blob/master/client.py

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
# import ROS
import json
# from core_tool import *
import lib.defaultpos as dp
import lib.base_geom as bg

#ROS side data request
pos = dict() #position info in the most recent frame of Leap
bpos = dict() #position info in the most recent frame of Baxter

class Client(object):
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        PeriodicCallback(self.tryAgain, 20000, io_loop=self.ioloop).start()
        self.ioloop.start()
        self.dl = dp.DefaultPos() #default left hand position
        self.dr = dp.DefaultPos("R") #default right hand position
        self.bdl = dp.BaxterDefaultPos() #Baxter default left hand position
        self.bdr = dp.BaxterDefaultPos("R") #Baxter default right hand position
        global pos, bpos
        pos["L"] = pos["R"] = bpos["L"] = bpos["R"] = []

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
        default_l.append(tf.transformations.quaternion_from_euler(self.dl.roll, self.dl.pitch, self.dl.yaw))
        delta_l = bg.TransformRightInv(current_l, default_l)

        current_r = pos["R"]
        default_r = [self.dr.x, self.dr.y, self.dr.z]
        default_r.append(tf.transformations.quaternion_from_euler(self.dr.roll, self.dr.pitch, self.dr.yaw))
        delta_r = bg.TransformRightInv(current_r, default_r)

        #scale delta_human to delta_baxter
        bdelta_l = dp.BaxterDefaultPos.scaleToBaxter(delta_l)
        bdelta_r = dp.BaxterDefaultPos.scaleToBaxter(delta_r)

        #calculate delta_baxter
        #not sure if the order of arguments to bg.Transform is correct
        bdefault_l = [self.bdl.x, self.bdl.y, self.bdl.z]
        bdefault_l.append(tf.transformations.quaternion_from_euler(self.bdl.roll, self.bdl.pitch, self.bdl.yaw))
        baxter_l = bg.Transform(bdefault_l, bdelta_l)

        bdefault_r = [self.bdr.x, self.bdr.y, self.bdr.z]
        bdefault_r.append(tf.transformations.quaternion_from_euler(self.bdr.roll, self.bdr.pitch, self.bdr.yaw))
        baxter_r = bg.Transform(bdefault_r, bdelta_r)

        #update Baxter position to move to (pos_baxter)
        bpos["L"] = baxter_l
        bpos["R"] = baxter_r


    @gen.coroutine
    def run(self):
        global pos
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
                a = list(map(lambda x: x.split("^"), msg.splitlines()))
                if (a[0][0].startswith("Left")): l = a[0]
                else: r = a[0]
                if (len(a) > 1 and a[1][0].startswith("Right")): r = a[1]
                elif (len(a) > 1): l = a[1]
                #get absolute 3-d coordinates
                pos["L"] = list(map(float, l[2][1:-1].split(",")))
                pos["R"] = list(map(float, r[2][1:-1].split(",")))
                #absolute Euler angles
                (lang, rang) = ([l[2][4], l[2][3], l[2][5]],
                                [r[2][4], r[2][3], r[2][5]])
                #pos["L"].append(lang)
                #pos["R"].append(rang)
                #transform Euler angles into Quaternion
                lquat = tf.transformations.quaternion_from_euler(lang[0], lang[1], lang[2])
                rquat = tf.transformations.quaternion_from_euler(rang[0], rang[1], rang[2])
                pos["L"].append(lquat)
                pos["R"].append(rquat)
                self.leap_to_baxter()


    def tryAgain(self):
        if self.ws is None:
            print("Lost connection. Trying to reconnect now...")
            self.connect()


def Run(t):
    global pos
    ql = t.robot.IK(bpos[“L”], arm=”LEFT”)
    qr = t.robot.IK(bpos[“R”], arm=”RIGHT”)
    print 'IK solution= {q}'.format(q=q)
    
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

def Run(t,*args):
  global bpos


if __name__ == "__main__":
    client = Client("ws://127.0.0.1:8888/ws", 5)
