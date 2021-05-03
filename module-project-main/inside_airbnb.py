import os
import json
import pandas as pd
from urllib.request import urlopen


class InsideAirBnB:
    """
    There are 7 data files available for every location and date
    These numbers are for New York City, 2021-02-04
                                                Size   ,   Shape            Key
    'data/listings.csv.gz',                     21.2 MB,   (18291, 74)      listings-dat
    'data/calendar.csv.gz',                     34.8 MB,   (13464021, 7)    calendar-dat
    'data/reviews.csv.gz',                      99.3 MB,   (847727, 6)      reviews-dat
    'visualisations/listings.csv',              5.12 MB,   (37012, 16)      listings-vis
    'visualisations/reviews.csv',               15.7 MB,   (847727, 2)      reviews-vis
    'visualisations/neighbourhoods.csv',       0.005 MB,   (230, 2)         neighborhoods-vis
    'visualisations/neighbourhoods.geojson',   0.604 MB,   (233, 3)         neighborhoods-geo
    """

    def __init__(self):
        self.locations = self.load_locations()

    def load_locations(self):
        cache_folder, index_filename = 'cache', 'inside-airbnb-locations.bz2'
        locations_path = os.path.join(cache_folder, index_filename)

        try:
            locations = pd.read_csv(locations_path)  # attempt to load from file
        except FileNotFoundError:
            print("Couldn't find the cached locations for insideairbnb.com, regenerating it...")

            # generate the cache folder if it's missing
            if not os.path.exists(cache_folder):
                os.mkdir(cache_folder)

            locations = self.regenerate_locations(save_path=locations_path)
        return locations

    def regenerate_locations(self, save_path=None):
        """
        Compiles a new index of locations and dates from insideairbnb.com
        :return: A pandas DataFrame of ['name', 'url', 'dates']
        TODO: This is slow because get_dates() searches all 148,121 lines of html * 109 locations.
        It would be more efficient to take note of line numbers between each location
        in the first pass. Then for urls and dates, pass in starting and ending line numbers
        to regextract() to only search the sections of the html for that location.
        Currently, this function takes ~17 seconds to finish.
        """
        import re
        import requests
        from collections import Counter

        # 148,121 of html as a list of strings
        html = requests.get('http://insideairbnb.com/get-the-data.html').text.splitlines()

        def regextract(pattern):
            # Searches 'html' and returns whatever is in the first () of pattern as a unique list of strings
            matches = [re.search(pattern, line) for line in html]  # non-matches are included as None
            matches = [match.group(1) for match in matches if match]  # the if filters out the None's
            return list(Counter(matches))  # Returns only unique matches. Preserves the original order

        def get_dates(location_url):
            """
            Finds all dates that insideairbnb.com has data for, given a location
            :param location_url: The place to get dates for in url form
            :return: A list of date strings in 'YYYY-MM-DD' form
            """
            location_url = f'http://data.insideairbnb.com/{location_url}/([\d\-]+)/'
            dates = regextract(pattern=location_url)
            return json.dumps(dates)

        # Construct the index dataframe
        locations = pd.DataFrame({
            'name': regextract(pattern='<h2>(.+)</h2>'),
            'url': regextract(pattern='insideairbnb.com/(.+)/[\d\-]+/data/listings')})
        locations['dates'] = locations['url'].apply(get_dates)

        # save index to a compressed form (to 14% the original size)
        # BZ2 compression performed better than ZIP, GZ and XZ in my trial
        locations.to_csv(save_path, index=False)
        return locations

    def get_location_names(self):
        return self.locations['name'].to_list()

    def get_location_urls(self):
        return self.locations['url'].to_list()

    def lookup(self, column, for_):
        # Given part of a place name, return the value in another column for that place
        # lookup(column='dates', for_='Francisco')
        hits = self.locations.name.str.contains(for_)
        if hits.sum() > 0:
            value = self.locations.at[hits.idxmax(), column]
            if column == 'dates':
                value = json.loads(value)
            return value
        else:
            print(f"Could not find {for_} in locations['name']")
            return None

    def get_data(self, location_name=None, date=None, data_files=None):
        # import geopandas as gpd

        if location_name:
            location_url = self.lookup(column='url', for_=location_name)
        else:
            location_name = 'New York City'
            location_url = 'united-states/ny/new-york-city'

        if date is None:  # if no date is provided, assume the most recent date (first in the list)
            date = self.lookup(column='dates', for_=location_name)[1]

        if data_files is None:
            data_files = [self.data_files[0]]

        domain = 'http://data.insideairbnb.com'
        place_date = '/'.join([domain, location_url, date])
        urls = ['/'.join([place_date, file]) for file in data_files]

        def load_df(url):
            filetype = url.split('.')[-1]

            if filetype in ['csv', 'gz']:
                df = pd.read_csv(url)  # compression format is inferred from the filename
            elif filetype == 'geojson':
                with urlopen(url) as response:
                    df = json.load(response)
            else:
                print(f"Can't load {url} as a DataFrame")
                df = None
            return df

        def df_name(url):
            filetype = url.split('.')[-1]
            table, mode = url.split('/')[-1:-3:-1]
            table = table.split('.')[0]
            mode = mode[:3]

            if filetype == 'geojson':
                return f'{table}-{filetype[:3]}'
            else:
                return f'{table}-{mode}'

        dataframes = {df_name(url): load_df(url) for url in urls}
        return dataframes
