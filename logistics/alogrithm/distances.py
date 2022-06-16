import numpy
import multiprocessing
from sklearn.neighbors import NearestNeighbors
from logistics.util import geometry, Heap, heap_min_comp
from logistics.objects import *

class PuiblicTransportDistanceMaster:
  def __init__(self, city_graph: CityGraph, n_neighbors=8):
    self.city_graph = city_graph
    X = numpy.array([[stop.longitude, stop.latitude] for _, stop in city_graph.stops])
    self.id_by_index = [stop_id for stop_id, _ in city_graph.stops]
    self.index_by_id = dict([(self.id_by_index[i], i) for i in range(len(self.id_by_index))])
    self.nearest_neighbours = NearestNeighbors(n_neighbors=n_neighbors).fit(X)
    self.precounted_neighbours = self.nearest_neighbours.kneighbors(X, return_distance=False)
    self.n_neighbors = n_neighbors

  def dijkstra_by_stops(self, point_a, point_b, need_path): # A-algorithm
    # i'm using flight time to point B as potential
    # point_a, point_b = numpy.array(point_a).ravel(), numpy.array(point_b).ravel()
    speed = {"flight":4*1000/60, "bus":60*1000/60, "train":90*1000/60, "subway":80*1000/60} # in meters in minute
    wait_time = {"bus":7, "train":15, "subway":4}
    pa_node = Node(longitude=point_a[0], latitude=point_a[1])
    pb_node = Node(longitude=point_b[0], latitude=point_b[1])
    
    queue = Heap(heap_min_comp)
    used_routes = set()
    used_nodes = set()
    f = dict() # evristc distance
    g = dict() # actual distance
    if need_path:
      parent = dict()
    def potential(node):
      return geometry.dist(pb_node, self.city_graph.stops[id]) / speed["flight"]
    flight_time = geometry.dist(pa_node, pb_node) / speed["flight"]
    if flight_time < 15:
      return flight_time, []
    indicies = self.nearest_neighbours.kneighbors([point_a], return_distance=False)
    for index in indicies[0]:
      id = self.id_by_index[index]
      f[id] = geometry.dist(pa_node, self.city_graph.stops[id]) / speed["flight"]
      g[id] = f[id] + potential(self.city_graph.stops[id])
      queue.add(g[id], id)
    b_closest = [self.id_by_index[i] for i in self.nearest_neighbours.kneighbors([point_b], return_distance=False)[0]]
    reached_b = 0
    while len(queue):
      cur_node_id = queue.get_best()[1]
      if cur_node_id in b_closest:
        reached_b += 1
        if reached_b == len(b_closest):
          break
      queue.delete_best()
      used_nodes.add(cur_node_id)
      cur_node = self.city_graph.stops[cur_node_id]
      for route_id in cur_node.related_relations:
        if route_id not in used_routes:
          used_routes.add(route_id)
          route = self.city_graph.routes[route_id]
          if route.tags["route"] not in speed:
            continue
          cur_node_order = route.related_nodes.index(cur_node_id)
          prev_node_id = cur_node_id
          cumulative_time = wait_time[route.tags["route"]]
          for next_node_order in range(cur_node_order + 1, len(route.related_nodes)):
            next_node_id = route.related_nodes[next_node_order]
            cumulative_time += geometry.dist(self.city_graph.stops[prev_node_id], 
                                             self.city_graph.stops[next_node_id]) / speed[route.tags["route"]]
            prev_node_id = next_node_id
            if next_node_id not in used_nodes:
              next_node_new_f = f[cur_node_id] + cumulative_time
              if next_node_id not in f or f[next_node_id] > next_node_new_f:
                f[next_node_id] = next_node_new_f
                g[next_node_id] = f[next_node_id] + potential(next_node_id)
                if need_path:
                  parent[next_node_id] = [cur_node_id, route_id, cur_node_order, next_node_order]
                if next_node_id in queue:
                  queue.change_by_value(g[next_node_id], next_node_id)
                else:
                  queue.add(g[next_node_id], next_node_id)
      switch_stops = [self.id_by_index[i] for i in self.precounted_neighbours[self.index_by_id[cur_node_id]]]
      for switch_stop_id in switch_stops:
        if switch_stop_id not in used_nodes:
          switch_stop_new_f = f[cur_node_id] + geometry.dist(self.city_graph.stops[switch_stop_id],
                                                             self.city_graph.stops[cur_node_id]) / speed["flight"]
          if switch_stop_id not in f or f[switch_stop_id] > switch_stop_new_f:
            f[switch_stop_id] = switch_stop_new_f
            g[switch_stop_id] = f[switch_stop_id] + potential(switch_stop_id)
            if need_path:
              parent[switch_stop_id] = [cur_node_id]
            if switch_stop_id in queue:
              queue.change_by_value(g[switch_stop_id], switch_stop_id)
            else:
              queue.add(g[switch_stop_id], switch_stop_id)
    dest_results = [f[i] + geometry.dist(self.city_graph.stops[i], pb_node) / speed["flight"] for i in b_closest if i in f]
    if len(dest_results) == 0 or min(dest_results) > flight_time:
      if need_path:
        return flight_time, []
      return flight_time
    if need_path:
      best_stop = numpy.argmin(dest_results)
      cur_stop_id = b_closest[best_stop]
      result_path = []
      while cur_stop_id in parent:
        parent_info = parent[cur_stop_id]
        if len(parent_info) == 1:
          cur_stop_id = parent_info[0]
        else:
          cur_stop_id = self.city_graph.routes[parent_info[1]].related_nodes[parent_info[2]]
          result_path.append(parent_info[1:])
      return dest_results[best_stop], result_path[::-1]
    return min(dest_results)

  def dijkstra_batch(self, points_a, points_b, need_path, pool_size=1):
    runs = []
    for point_a in points_a:
      for point_b in points_b:
        runs.append([point_a, point_b, need_path])
    with multiprocessing.Pool(pool_size) as p:
      tmp_result = p.starmap(self.dijkstra_by_stops, runs)
    if need_path:
      result_dist = [[tmp_result[i * len(points_b) + j][0] for j in range(len(points_b))] for i in range(len(points_a))]
      result_path = [[tmp_result[i * len(points_b) + j][1] for j in range(len(points_b))] for i in range(len(points_a))]
      return result_dist, result_path
    result = [[tmp_result[i * len(points_b) + j] for j in range(len(points_b))] for i in range(len(points_a))]
    return result

  def dijkstra_batch_pairs(self, points_a, points_b, need_path, pool_size=1):
    runs = []
    for i in range(len(points_a)):
        runs.append([points_a[i], points_b[i], need_path])
    with multiprocessing.Pool(pool_size) as p:
      tmp_result = p.starmap(self.dijkstra_by_stops, runs)
    if need_path:
      result_dist = [tmp_result[i][0] for i in range(len(points_a))]
      result_path = [tmp_result[i][1] for i in range(len(points_a))]
      return result_dist, result_path
    result = [tmp_result[i] for i in range(len(points_a))]
    return result