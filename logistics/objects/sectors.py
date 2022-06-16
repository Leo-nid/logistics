import numpy
import random
import math
from .storage import Storage


eps = 1e-6

def get_min(field_name, *storages):
  result = None
  for storage in storages:
    for _, item in storage:
      if result is None:
        result = getattr(item, field_name)
      else:
        result = min(result, getattr(item, field_name))
  return result

def get_max(field_name, *storages):
  result = None
  for storage in storages:
    for _, item in storage:
      if result is None:
        result = getattr(item, field_name)
      else:
        result = max(result, getattr(item, field_name))
  return result


attract_by_level = numpy.arange(115) ** 2

def get_attractiveness_by_level(level):
  try:
    return attract_by_level[int(float(level))]
  except ValueError:
    return 2

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
    self.sectors_prefix_attract = [[[[0], [0]] for j in range(height)] for i in range(width)]
    self.sectors_buildings_ids = [[[[], []] for j in range(height)] for i in range(width)]
    self.prefix_sums = [[0], [0]]
    self.sectors_stops = [[Storage() for j in range(height)] for i in range(width)]
    self.min_coords = (get_min("longitude", accommodation_buildings, commercial_buildings, stops) - eps,
                       get_min("latitude", accommodation_buildings, commercial_buildings, stops) - eps)
    self.max_coords = (get_max("longitude", accommodation_buildings, commercial_buildings, stops) + eps,
                       get_max("latitude", accommodation_buildings, commercial_buildings, stops) + eps)
    self.lon_interval = (self.max_coords[0] - self.min_coords[0]) / width
    self.lat_interval = (self.max_coords[1] - self.min_coords[1]) / height
    self.buildings = [accommodation_buildings, commercial_buildings]

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
        self.sectors_prefix_attract[lon_sector_id][lat_sector_id][b_type].append(self.sectors_prefix_attract[lon_sector_id][lat_sector_id][b_type][-1] + 
                                                                                 get_attractiveness_by_level(building.tags["building:levels"]))
        self.sectors_buildings_ids[lon_sector_id][lat_sector_id][b_type].append(building.id)
    for i in range(self.width):
      for j in range(self.height):
        self.prefix_sums[b_type].append(self.prefix_sums[b_type][-1] + self.sectors_attract[i][j][b_type])

  def fill_sector_stops(self, stops):
    for _, stop in stops:
      lon_sector_id, lat_sector_id = self.get_sector_by_coords(stop.longitude, stop.latitude)
      self.sectors_attract[lon_sector_id][lat_sector_id].add(stop)

  def get_sector_stops(self, longitude, latitude):
    lon_sector_id, lat_sector_id = self.get_sector_by_coords(longitude, latitude)
    if 0 <= lon_sector_id < self.width and 0 <= lat_sector_id < self.height:
      return self.sectors_stops[lon_sector_id][lat_sector_id]
    return Storage()

  def get_random_points(self, num_points, type):
    coords = []
    for i in range(num_points):
      random_sector_point = random.randint(0, self.prefix_sums[type][-1] - 1)
      sector_id = numpy.searchsorted(self.prefix_sums[0], random_sector_point, side='right') - 1
      sector_id_i, sector_id_j = sector_id // self.height, sector_id % self.height
      random_building_point = random.randint(0, self.sectors_prefix_attract[sector_id_i][sector_id_j][type][-1] - 1)
      building_index = numpy.searchsorted(self.sectors_prefix_attract[sector_id_i][sector_id_j][type], random_building_point, side='right') - 1
      building_id = self.sectors_buildings_ids[sector_id_i][sector_id_j][type][building_index]
      building = self.buildings[type][building_id]
      coords.append([building.longitude, building.latitude])
    return coords