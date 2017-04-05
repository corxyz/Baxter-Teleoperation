#modified from https://github.com/ilkerkesen/tornado-websocket-client-example/blob/master/client.py

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
# import ROS
import json
# from core_tool import *
import lib.defaultpos as dp


#ROS side data request
pos = dict() #position info in the most recent frame
dispos = dict() #disposition info from the most recent frame

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
        dispos["L"] = [dl.x, dl.y, dl.z, dl.roll, dl.pitch, dl.yaw]
        dispos["R"] = [dr.x, dr.y, dr.z, dr.roll, dr.pitch, dr.yaw]


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

    #disposition calculation (updates list with 7 elements)
    def calc_desposition(self, lco, rco, lang, rang):
        global dispos
        dispos["L"][0] = lco[0] - self.dl.x
        dispos["L"][1] = lco[1] - self.dl.y
        dispos["L"][2] = lco[2] - self.dl.z
        dispos["L"][3] = lang[0] - self.dl.roll
        dispos["L"][4] = lang[1] - self.dl.pitch
        dispos["L"][5] - lang[2] - self.dl.yaw
        dispos["R"][0] = rco[0] - self.dr.x
        dispos["R"][1] = rco[1] - self.dr.y
        dispos["R"][2] = rco[2] - self.dr.z
        dispos["R"][3] = rang[0] - self.dr.roll
        dispos["R"][4] = rang[1] - self.dr.pitch
        dispos["R"][5] - rang[2] - self.dr.yaw

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
                a = list(map(lambda x: x.split("^"), msg.splitlines())
                (l, r) = (dispos{"L"}, dispos["R"]) #init
                if (a[0][0].startswith("Left")): l = a[0]
                else: r = a[0]
                if (len(a) > 1 and a[1][0].startswith("Right")): r = a[1]
                else if (len(a) > 1): l = a[1] 
                #get absolute 3-d coordinates
                pos["L"] = list(map(float, l[2][1:-1].split(",")))
                pos["R"] = list(map(float, r[2][1:-1].split(",")))
                #absolute Euler angles
                (lang, rang) = ([l[2][4], l[2][3], l[2][5]], 
                                [r[2][4], r[2][3], r[2][5])
                pos["L"].append(lang)
                pos["R"].append(rang)
                dispos = self.calc_disposition(lpos, lang, rpos, rang)


    def tryAgain(self):
        if self.ws is None:
            print("Lost connection. Trying to reconnect now...")
            self.connect()


def Run(t):
    global pos
    # def moveArm(*args):
    #     arm= args[0]
    #     dp= args[1]
    #     x= list(t.robot.FK(arm=arm))  #Current end-effector pose
    #     x_trg= [x[d]+dp[d] for d in range(3)] + x[3:]  #Target
    #     print 'Moving {arm}-arm to {x}'.format(arm=LRToStr(arm), x=x_trg)
    #     t.robot.MoveToX(x_trg, dt=4.0, arm=arm)

    #transform Euler angles into Quaternion
    lpos = pos["L"]
    rpos = pos["R"]
    lquat = tf.transformations.quaternion_from_euler(lpos[3], lpos[4], lpos[5])
    lquat = tf.transformations.quaternion_from_euler(rpos[3], rpos[4], rpos[5])
    #TODO: use Quaternion & coordinates to control Baxter

    while(len(pos) != 0):
        if(pos[0] != "Right hand"):
            println("RIGHT HAND: "  + d) #?
            # moveArm("RIGHT", d['Right hand'])
        if(pos[0] != "Left hand"):
            println("LEFT: "  + d)
            # moveArm("LEFT", d['Left hand'])

if __name__ == "__main__":
    client = Client("ws://127.0.0.1:8888/ws", 5)
