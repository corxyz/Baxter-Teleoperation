import math

class DefaultPos(object):

        def __init__(self, handType="L"):
                if (handType == "L"): c = 1
                else: c = -1
                self.x = 0
                self.y = 300
                self.z = 0
                self.roll = math.pi/2
                self.pitch = 0
                self.yaw = 0
