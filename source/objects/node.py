import uuid
from node_diff import NodeDiff

class Node:
  def __init__(self, latitude = 0, longitude = 0, **kwargs):
    if kwargs["id"]:
      self.id = kwargs["id"]
    else:
      self.id = uuid.uuid4()
    self.latitude = latitude
    self.longitude = longitude
    self.related_ways = set()
    self.related_relations = set()

  def __sub__(self, oth):
    return NodeDiff(self.latitude - oth.latitude, self.longitude - oth.longitude)

  def __add__(self, oth):
    return Node(self.latitude + oth.latitude, self.longitude + oth.longitude)