import math
import sys
sys.path.insert(0, '../')

#import Leap
#from SampleGiada import SampleListener

#ib = Leap.Controller().frame().interaction_box

class DefaultPos(object):

        def __init__(self, handType="L"):
                if (handType == "L"): c = 1
                else: c = -1
                self.x = 0
                self.y = 30 * c / 1000
                self.z = 200-235/2000 #bottom of the interaction box
                self.roll = 0
                self.pitch = 0
                self.yaw = 0


class BaxterDefaultPos(object):

#        xRange = (0, ib.depth*6.5)
 #       yRange = (-(ib.width/2)*11, (ib.width/2)*11)
  #      zRange = (0, ib.height*6.05)

        xscale = 0.01
        yscale = 0.01
        zscale = 0.01

        def __init__(self, handType="L"):
                if (handType == "L"): c = 1
                else: c = -1
                self.x = 0
                self.y = 30 * BaxterDefaultPos.yscale * c / 1000
                self.z = (200-235/2)*BaxterDefaultPos.zscale/1000
                self.roll = 0
                self.pitch = 0
                self.yaw = 0

        @staticmethod
        def scaleToBaxter(delta):
                print "delta0: "
                print delta
                newx = (delta[0] + 147.0/2) * BaxterDefaultPos.xscale / 1000
                newy = delta[1] * BaxterDefaultPos.yscale / 1000
                newz = delta[2] * BaxterDefaultPos.zscale / 1000
                bdelta = [newx, newy, newz]
                bdelta += delta[3:]
                print "bdelta: "
                print bdelta
                return bdelta
