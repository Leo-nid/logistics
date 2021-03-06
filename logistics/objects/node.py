import uuid
import math

class Node:
  def __init__(self, latitude = 0, longitude = 0, **kwargs):
    if "id" in kwargs:
      self.id = kwargs["id"]
    else:
      self.id = uuid.uuid4()
    self.latitude = float(latitude)
    self.longitude = float(longitude)
    self.related_ways = set()
    self.related_relations = set()
    if "tags" in kwargs:
      self.tags = kwargs["tags"]

  def __sub__(self, oth):
    return NodeDiff(self.latitude - oth.latitude, self.longitude - oth.longitude)

  def __add__(self, oth):
    return Node(self.latitude + oth.latitude, self.longitude + oth.longitude)


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