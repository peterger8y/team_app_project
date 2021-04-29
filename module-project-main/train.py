from inside_airbnb import InsideAirBnB

locations = InsideAirBnB()
list_locations = list(locations.load_locations().get('name'))

print(list_locations)