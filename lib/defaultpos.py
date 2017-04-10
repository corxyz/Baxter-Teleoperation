import math
import Leap.InteractionBox as ib

class DefaultPos(object):

        def __init__(self, handType="L"):
                if (handType == "L"): c = 1
                else: c = -1
                self.x = 0
                self.y = 30 * c
                self.z = 20-ib.height/2 #bottom of the interaction box
                self.roll = 0
                self.pitch = 0
                self.yaw = 0


class BaxterDefaultPos(object):

        xRange = (0, ib.depth*6.5)
        yRange = (-(ib.width/2)*11, (ib.width/2)*11)
        zRange = (0, ib.height*6.05)

        xscale = 6.5
        yscale = 11.0
        zscale = 6.05

        def __init__(self, handType="L"):
                if (handType == "L"): c = 1
                else: c = -1
                self.x = 0
                self.y = 30 * 11 * c
                self.z = (20-ib.height/2)*6.05
                self.roll = 0
                self.pitch = 0
                self.yaw = 0

        @staticmethod
        def scaleToBaxter(delta):
                newx = (delta[0] + ib.depth/2) * BaxterDefaultPos.xscale
                newy = delta[1] * BaxterDefaultPos.yscale
                newz = delta[2] * BaxterDefaultPos.zscale
                bdelta = [newx, newy, newz]
                bdelta.append(delta[3:])
                return bdelta
