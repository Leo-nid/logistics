from logistics.objects.node import Node
from logistics.objects.way import Way
from logistics.objects.street import Street

class Stop(Node):
  def __init__(self, street_id = None, direction = 0, segment = -1, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.street_id = street_id
    self.direction = direction
    self.segment = -1