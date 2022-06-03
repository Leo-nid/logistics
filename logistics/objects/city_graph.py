from logistics.objects.storage import Storage

class CityGraph:
  def __init__(self, 
               crossroads:Storage = Storage(), 
               streets:Storage = Storage(), 
               stops:Storage = Storage(),
                haversine=True):
    self.crossroads = crossroads
    self.streets = streets
    self.stops = stops
    self.haversine = haversine