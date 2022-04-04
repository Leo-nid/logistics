import math
from node import Node

class NodeDiff:
  def __init__(self, latitude = 0, longitude = 0):
    self.latitude = latitude
    self.longitude = longitude

  def length(self):
    return math.hypot(self.latitude, self.longitude)

  def __mul__(self, oth):
    return NodeDiff(self.latitude * oth, self.longitude * oth)

  def __rmul__(self, oth):
    return self * oth