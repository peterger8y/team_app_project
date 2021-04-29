from .inside_airbnb import InsideAirBnB
import pandas as pd

locations = InsideAirBnB()
list_locations = list(locations.load_locations().get('name'))


def neighbourhood_function(alpha):
    locations = InsideAirBnB()
    delta = locations.get_data(location_name=alpha, date=None, data_files=['data/listings.csv.gz'])
    epsilon = delta['listings-dat']['neighbourhood_cleansed']
    zeta = pd.DataFrame(epsilon.value_counts()).index
    return zeta

# if __name__ == "__main__":
# for x in beta:

def get_at_it(location):
    locations = InsideAirBnB()
    omega = locations.get_data(location_name=location, date=None, data_files=['data/listings.csv.gz'])
    kappa = omega['listings-dat']
    return kappa