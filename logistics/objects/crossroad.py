from logistics.objects.node import Node

class Crossroad(Node):
  def __init__(self, latency = 30):
    super.__init__()
    self.latency = latency