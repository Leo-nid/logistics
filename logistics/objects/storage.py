from logistics.objects.node import Node
from logistics.objects.stop import Stop
from logistics.objects.way import Way
from logistics.objects.relation import Relation

class Storage:
  def __init__(self):
    self.container = {}

  def add(self, object):
    if type(object) not in [Node, Way, Stop, Relation]:
      raise RuntimeError("kek")
    self.container[object.id] = object

  def remove(self, objcet_id):
    self.container.pop(objcet_id)

  def __len__(self):
    return len(self.container)

  def __iter__(self):
    return self.container.items().__iter__()

  def __getitem__(self, key):
    if key not in self.container:
      raise RuntimeError("there is no object with key {}".format(key))
    return self.container[key]

  def __contains__(self, key):
    return (key in self.container)