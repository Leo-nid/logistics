import math
import pandas

from logistics.objects import *
from logistics.util import geometry

def calculate_related_street_to_stop(stop:Stop, city_graph: CityGraph):
  closest_crossroads = sorted(list(city_graph.crossroads.container.items()), lambda x: geometry.dist(stop, x[1]))[:10]
  closest_road_dist = None
  closest_road_info = None
  closest_ways = set()
  for crossroad in closest_crossroads:
    closest_ways |= crossroad[1].related_ways
  for way in crossroad[1].related_ways:
    if isinstance(way, Street):
      for ind in range(len(way.nodes_id) - 1):
          node1, node2 = city_graph.crossroads[way.nodes_id[ind]], city_graph.crossroads[way.nodes_id[ind + 1]]
          segment_info = geometry.dist_to_segment(stop, [node1, node2], city_graph.haversine)
          if closest_road_dist is None or segment_info[1] < closest_road_dist:
            closest_road_dist = segment_info[1]
            closest_road_info = [way.id, segment_info[2], ind]
  if closest_road_info is not None:
    stop.street_id, stop.direction, stop.segment = closest_road_info

def match_stops(stops: Storage, dataframe, max_dist = 10, sector_size = 10):
  eps = 1e-6
  min_lon, max_lon = dataframe["lon"].min() - eps, dataframe["lon"].max() + eps
  min_lat, max_lat = dataframe["lat"].min() - eps, dataframe["lat"].max() + eps
  dataframe["stop_id_osm"] = [0] * len(dataframe)
  lon_sectors = int(geometry.dist(Node(latitude=min_lat, longitude=min_lon),
                                  Node(latitude=min_lat, longitude=max_lon)) / (max_dist * sector_size)) + 1
  lon_interval = (max_lon - min_lon) / lon_sectors
  lat_sectors = int(geometry.dist(Node(latitude=min_lat, longitude=min_lon),
                                  Node(latitude=max_lat, longitude=min_lon)) / (max_dist * sector_size)) + 1
  lat_interval = (max_lat - min_lat) / lat_sectors
  sectors = [[Storage() for j in range(lat_sectors)] for i in range(lon_sectors)]
  for _, stop in stops:
    lon_sector_id = int(math.floor((stop.longitude - min_lon) / lon_interval))
    lat_sector_id = int(math.floor((stop.latitude - min_lat) / lat_interval))
    if 0 <= lon_sector_id < lon_sectors and 0 <= lat_sector_id < lat_sectors:
      sectors[lon_sector_id][lat_sector_id].add(stop)
    if lon_sector_id >= 0 and geometry.dist(Node(latitude=stop.latitude, longitude=min_lon+lon_interval*lat_sector_id),
                                            stop) <= max_dist:
      sectors[lon_sector_id - 1][lat_sector_id].add(stop)
    if lon_sector_id < lon_sectors - 1 and geometry.dist(Node(latitude=stop.latitude, longitude=min_lon+lon_interval*(lat_sector_id+1)),
                                                          stop) <= max_dist:
      sectors[lon_sector_id + 1][lat_sector_id].add(stop)
    if lat_sector_id >= 0 and geometry.dist(Node(latitude=min_lat+lat_interval*lat_sector_id, longitude=stop.longitude),
                                            stop) <= max_dist:
      sectors[lon_sector_id][lat_sector_id - 1].add(stop)
    if lat_sector_id < lat_sectors - 1 and geometry.dist(Node(latitude=min_lat+lat_interval*(lat_sector_id+1), longitude=stop.longitude),
                                                          stop) <= max_dist:
      sectors[lon_sector_id][lat_sector_id + 1].add(stop)
  for index in dataframe.index:
    cur_lon = dataframe.loc[index, 'lon']
    cur_lat = dataframe.loc[index, 'lat']
    lon_sector_id = int(math.floor((cur_lon - min_lon) / lon_interval))
    lat_sector_id = int(math.floor((cur_lat - min_lat) / lat_interval))
    for _, sector_stop in sectors[lon_sector_id][lat_sector_id]:
      print(geometry.dist(Node(latitude=cur_lat, longitude=cur_lon), sector_stop))
      if geometry.dist(Node(latitude=cur_lat, longitude=cur_lon), sector_stop) < max_dist:
        dataframe.loc[index, 'stop_id_osm'] = sector_stop.id
  return dataframe