from logistics.objects import *
import math
import haversine

def dist(node_lhs: Node, node_rhs: Node, haversine = True):
  if haversine:
    return haversine.haversine((node_lhs.latitude, node_rhs.longitude), (node_rhs.latitude, node_rhs.longitude), unit=haversine.Unit.KILOMETERS)
  return (node_lhs - node_rhs).length()

def dot_product(diff_lhs: NodeDiff, diff_rhs: NodeDiff):
  return diff_lhs.latitude * diff_rhs.latitude + diff_lhs.longitude * diff_rhs.longitude

def cross_product(diff_lhs: NodeDiff, diff_rhs: NodeDiff):
  return diff_lhs.latitude * diff_rhs.longitude - diff_lhs.longitude * diff_rhs.latitude

def dist_to_segment(stop_lhs: Node, nodes: list[Node], haversine = True):
  dp = dot_product(nodes[1] - nodes[0], stop_lhs - nodes[0])
  sgn = math.copysign(1, cross_product(nodes[1] - nodes[0], stop_lhs - nodes[0]))
  if dp >= 0 and dot_product(nodes[0] - nodes[1], stop_lhs - nodes[1]):
    part = dp / (nodes[1] - nodes[0]).length() ** 2
    closest_point = nodes[0] + part * (nodes[1] - nodes[0])
    return part, dist(stop_lhs, closest_point, haversine), sgn
  else:
    dsts = [dist(stop_lhs, nodes[i]) for i in range(2)]
    return int(dsts[0] > dsts[1]), min(dsts), sgn