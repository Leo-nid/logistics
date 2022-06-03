import numpy
import math
from .storage import Storage


eps = 1e-6

def get_min(storage, field_name):
  result = None
  for _, item in storage:
    if result is None:
      result = item.getattr(field_name)
    else:
      result = min(item.getattr(field_name))

def get_max(field_name, *storages):
  result = None
  for storage in storages:
    for _, item in storage:
      if result is None:
        result = getattr(item, field_name)
      else:
        result = max(getattr(item, field_name))
  return result


attract_by_level = numpy.logspace(0, 3.5, 110)

def get_attractiveness_by_level(level):
  return attract_by_level[level]

class Sectors:
  def __init__(self,
               width,
               height,
               accommodation_buildings: Storage, 
               commercial_buildings: Storage, 
               stops: Storage):
    self.height = height
    self.width = width
    self.sectors_attract = [[[0, 0] for j in range(height)] for i in range(width)] #accom, comm
    self.sectors_stops = [[Storage() for j in range(height)] for i in range(width)]
    self.min_coords = (get_min("longitude", accommodation_buildings, commercial_buildings, stops) - eps,
                       get_min("latitude", accommodation_buildings, commercial_buildings, stops) - eps)
    self.max_coords = (get_min("longitude", accommodation_buildings, commercial_buildings, stops) + eps,
                       get_min("latitude", accommodation_buildings, commercial_buildings, stops) + eps)
    self.lon_interval = (self.max_coords[0] - self.min_coords[0]) / width
    self.lat_interval = (self.max_coords[1] - self.min_coords[1]) / height

    self.fill_sectors_attract_with_buildings(accommodation_buildings, 0)
    self.fill_sectors_attract_with_buildings(commercial_buildings, 1)

  def get_sector_by_coords(self, longitude, latitude):
      lon_sector_id = int((longitude - self.min_coords[0]) / self.lon_interval)
      lat_sector_id = int((latitude - self.min_coords[1]) / self.lat_interval)
      return lon_sector_id, lat_sector_id

  def fill_sectors_attract_with_buildings(self, buildings: Storage, b_type):
    for _, building in buildings:
      if "building:levels" in building.tags:
        lon_sector_id, lat_sector_id = self.get_sector_by_coords(building.longitude, building.latitude)
        self.sectors_attract[lon_sector_id][lat_sector_id][b_type] += get_attractiveness_by_level(building.tags["building:levels"])

  def fill_sector_stops(self, stops):
    for _, stop in stops:
      lon_sector_id, lat_sector_id = self.get_sector_by_coords(stop.longitude, stop.latitude)
      self.sectors_attract[lon_sector_id][lat_sector_id].add(stop)

  def get_sector_stops(self, longitude, latitude):
    lon_sector_id, lat_sector_id = self.get_sector_by_coords(longitude, latitude)
    if 0 <= lon_sector_id < self.width and 0 <= lat_sector_id < self.height:
      return self.sectors_stops[lon_sector_id][lat_sector_id]
    return Storage()