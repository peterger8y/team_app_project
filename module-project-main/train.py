from .inside_airbnb import InsideAirBnB
import pandas as pd
import geopandas as gpd

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

def get_at_it(location, geo=False):
    locations = InsideAirBnB()
    if geo:
        scepter = locations.get_data(location_name=location, date=None, data_files=['visualisations/listings.csv'])
        geo_df = scepter['listings-vis']
        eighty = locations.get_data(location_name=location, date=None, data_files=['visualisations/neighbourhoods.geojson'])
        #alpha = eighty['neighborhoods-geo']
        geo_df = geo_df.groupby(by=["neighbourhood"]).mean()

        return eighty['neighbourhoods-geo'], geo_df
    omega = locations.get_data(location_name=location, date=None, data_files=['data/listings.csv.gz'])
    kappa = omega['listings-dat']

    return kappa
