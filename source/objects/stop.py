from node import Node
from way import Way
from street import Street
from util.city_graph import CityGraph
from util import geometry

class Stop(Node):
  def __init__(self, street_id = None, direction = 0, segment = -1, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.street_id = street_id
    self.direction = direction
    self.segment = -1

  def calculate_related_street(self, city_graph: CityGraph):
    closest_crossroads = sorted(list(city_graph.crossroads.container.items()), lambda x: geometry.dist(self, x[1]))[:10]
    closest_road = None
    closest_road_info = None
    for crossroad in closest_crossroads:
      for way in crossroad[1].related_ways:
        if isinstance(way, Street):
          for 