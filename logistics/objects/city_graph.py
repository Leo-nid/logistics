from logistics.objects.storage import Storage

class CityGraph:
  def __init__(self, 
               crossroads:Storage = Storage(), 
               streets:Storage = Storage(), 
               stops:Storage = Storage(),
               routes:Storage = Storage(),
               haversine=True):
    self.crossroads = crossroads
    self.streets = streets
    self.stops = stops
    self.routes = routes
    self.haversine = haversine