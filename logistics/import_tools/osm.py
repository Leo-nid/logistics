import numpy
import xml.etree.ElementTree

from logistics.util.city_graph import CityGraph
from logistics.util.storage import Storage
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
  buildings = Storage()

  for elem in root:
    if elem.tag == "node":
      is_stop = False
      for tags in root:
        if tags.tag == "tag" and tags["k"] == "highway" and tags["v"] == "bus_stop":
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
          elif way_piece.attrib["k"] == "building":
            is_building = True
          another_tags[way_piece.attrib["k"]] = way_piece.attrib["v"]
        elif way_piece.tag == "nd":
          connected_nodes.append(way_piece.attrib["ref"])
      if is_road:
        for node_id in connected_nodes:
          crossroads.add(nodes[node_id])
        streets.add(Way(id=elem.attrib["id"], nodes_id=connected_nodes, node_storage=crossroads))
      elif is_building:
        aprox_lon = numpy.array([float(nodes[id].longitude) for id in connected_nodes]).mean()
        aprox_lat = numpy.array([float(nodes[id].latitude) for id in connected_nodes]).mean()
        buildings.add(Way(id=elem.attrib["id"], 
                          nodes_id=connected_nodes, 
                          tags={"lat":aprox_lat, "lon":aprox_lon, **another_tags}))
  city_graph = CityGraph(crossroads, streets, stops)
  return city_graph, buildings