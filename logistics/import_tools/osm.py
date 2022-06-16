import numpy
import xml.etree.ElementTree

from logistics.objects import *


highway_is_road = ["motorway", 
                   "trunk",
                   "primary",
                   "secondary",
                   "tertiary",
                   "unclassified",
                   "residential",
                   "motorway_link",
                   "trunk_link",
                   "primary_link",
                   "secondary_link",
                   "tertiary_link",
                   "bus_guideway",
                   "road",
                   "busway"]

def from_xml(path):
  tree = xml.etree.ElementTree.parse(path)
  root = tree.getroot()

  nodes = Storage()
  stops = Storage()
  crossroads = Storage()
  streets = Storage()
  routes = Storage()
  buildings = Storage()

  for elem in root:
    if elem.tag == "node":
      is_stop = False
      for tags in elem:
        if tags.tag == "tag" and tags.attrib["k"] == "highway" and tags.attrib["v"] == "bus_stop":
          is_stop = True
        elif tags.tag == "tag" and tags.attrib["k"] == "railway" and tags.attrib["v"] in ["station", "stop"]:
          is_stop = True
      if is_stop:
        stops.add(Stop(id=elem.attrib["id"], latitude=elem.attrib["lat"], longitude=elem.attrib["lon"]))
      else:
        nodes.add(Node(id=elem.attrib["id"], latitude=elem.attrib["lat"], longitude=elem.attrib["lon"]))

    elif elem.tag == "way":
      is_road = False
      is_building = False
      connected_nodes = []
      another_tags = {}
      for way_piece in elem:
        if way_piece.tag == "tag":
          if way_piece.attrib["k"] == "highway" and way_piece.attrib["v"] in highway_is_road:
            is_road = True
          elif way_piece.attrib["k"] == "building" or way_piece.attrib["k"] == "amenity":
            is_building = True
          another_tags[way_piece.attrib["k"]] = way_piece.attrib["v"]
        elif way_piece.tag == "nd":
          if way_piece.attrib["ref"] in nodes:
            connected_nodes.append(way_piece.attrib["ref"])
      if is_road:
        for node_id in connected_nodes:
          if node_id in nodes:
            crossroads.add(nodes[node_id])
            nodes[node_id].related_ways.add(elem.attrib["id"])
        streets.add(Way(id=elem.attrib["id"], nodes_id=connected_nodes, node_storage=crossroads))
      elif is_building:
        aprox_lon = numpy.array([float(nodes[id].longitude) for id in connected_nodes if id in nodes]).mean()
        aprox_lat = numpy.array([float(nodes[id].latitude) for id in connected_nodes if id in nodes]).mean()
        buildings.add(Node(id=elem.attrib["id"], 
                           longitude=aprox_lon,
                           latitude=aprox_lat,
                           nodes_id=connected_nodes, 
                           tags=another_tags))

    elif elem.tag == "relation":
      is_route = False
      rel_stops = []
      another_tags = {}
      for rel_piece in elem:
        if rel_piece.tag == "tag":
          if rel_piece.attrib["k"] == "type" and rel_piece.attrib["v"] == "route":
            is_route = True
          another_tags[rel_piece.attrib["k"]] = rel_piece.attrib["v"]
        elif rel_piece.tag == "member" and rel_piece.attrib["type"] == "node" and rel_piece.attrib["role"] in ["stop", "stop_exit_only", "stop_entry_only"]:
          if rel_piece.attrib["ref"] in stops:
            rel_stops.append(rel_piece.attrib["ref"])
      if is_route:
        routes.add(Relation(id=elem.attrib["id"], related_nodes=rel_stops, tags=another_tags))
        for stop_id in rel_stops:
          if stop_id in stops:
            stops[stop_id].related_relations.add(elem.attrib["id"])
  city_graph = CityGraph(crossroads, streets, stops, routes)
  return city_graph, buildings