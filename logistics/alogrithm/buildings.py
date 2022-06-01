import pandas
import numpy

from logistics.objects import *
from logistics.util.storage import Storage


accommodation = [
  "apartments",
  "barracks",
  "bungalow",
  "cabin",
  "detached",
  "dormitory",
  "farm",
  "ger",
  "hotel",
  "house",
  "houseboat",
  "residential",
  "semidetached_house",
  "static_caravan",
  "terrace"
]

commercial = [
  "commercial",
  "industrial",
  "kiosk",
  "office",
  "retail",
  "supermarket",
  "warehouse"
]


def separate_buildings(buildings: Storage):
  accommodation_buildings = Storage()
  commercial_buildings = Storage()
  for _, building in buildings:
    if building.tags["building"] in accommodation or building.tags["building"] == "yes":
      accommodation_buildings.add(building)
    elif building.tags["building"] in commercial:
      commercial_buildings.add(building)
  return accommodation_buildings, commercial_buildings


def from_storage_ways(storage, columns = []):
    dct = {}
    for column in columns:
        dct[column] = []
    for _, item in storage:
        for column_name in columns:
            if column_name in item.tags:
                dct[column_name].append(item.tags[column_name])
            elif column_name == "id":
                dct[column_name].append(item.id)
            else:
                dct[column_name].append(numpy.nan)
    return pandas.DataFrame(dct)