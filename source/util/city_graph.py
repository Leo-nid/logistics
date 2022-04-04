from ..objects import *
from storage import Storage

class CityGraph:
  def __init__(self):
    self.crossroads = Storage()
    self.streets = Storage()
    self.stops = Storage()
    self.haversine = True