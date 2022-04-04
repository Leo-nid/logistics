from ..objects import Node, Way

class Storage:
  def __init__(self):
    self.container = {}

  def add(self, object):
    if type(object) not in [Node, Way]:
      raise RuntimeError("kek")
    self.container[object.id] = object

  def remove(self, objcet_id):
    self.container.pop(objcet_id)

  def __getitem__(self, key):
    if key not in self.container:
      raise RuntimeError("there is no object with key {}".format(key))
    return self.container[key]