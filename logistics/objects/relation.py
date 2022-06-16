import uuid
from .way import Way
from .node import Node

class Relation:
  def __init__(self, related_nodes = [], related_ways=[], tags={}, **kwargs):
    if "id" in kwargs:
        self.id = kwargs["id"]
    else:
      self.id = uuid.uuid4()
    self.related_nodes = related_nodes
    self.related_ways = related_ways
    self.tags = tags