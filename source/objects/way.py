import uuid
from .node import Node

class Way:
  def __init__(self, nodes_id = [], *args, **kwargs):
    if kwargs["id"]:
      self.id = kwargs["id"]
    else:
      self.id = uuid.uuid4()
    self.nodes_id = nodes_id
    if kwargs["node_storage"]:
      for node_id in self.nodes_id:
        kwargs["node_storage"][node_id].related_ways.add(self.id)