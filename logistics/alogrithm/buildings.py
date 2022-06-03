import pandas
import numpy

from logistics.objects import *


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

civic = [
  "bakehouse",
  "civic",
  "college",
  "fire_station",
  "government",
  "hospital",
  "kindergarten",
  "public",
  "school",
  "toilets",
  "train_station",
  "transportation",
  "university"
]

amenity_sustenance = [
  "bar",
  "biergarten",
  "cafe",
  "fast_food",
  "food_court",
  "ice_cream",
  "pub",
  "restaurant"
]

amenity_education = [
  "college",
  "driving_school",
  "kindergarten",
  "language_school",
  "library",
  "toy_library",
  "music_school",
  "school",
  "university"
]

amenity_healthcare = [
  "baby_hatch",
  "clinic",
  "dentist",
  "doctors",
  "hospital",
  "nursing_home",
  "pharmacy",
  "social_facility",
  "veterinary"
]


def separate_buildings(buildings: Storage):
  accommodation_buildings = Storage()
  commercial_buildings = Storage()
  for _, building in buildings:
    if "amenity" in building.tags and building.tags["amenity"] in amenity_education + amenity_healthcare + amenity_sustenance:
      commercial_buildings.add(building)
    elif "building" in building.tags and building.tags["building"] in accommodation or building.tags["building"] == "yes":
      accommodation_buildings.add(building)
    elif "building" in building.tags and building.tags["building"] in commercial + civic:
      commercial_buildings.add(building)
  return accommodation_buildings, commercial_buildings


def dataframe_from_storage_ways(storage, columns = []):
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