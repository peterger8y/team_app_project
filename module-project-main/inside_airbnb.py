import os
import pandas as pd


class InsideAirBnB:
    def __init__(self):
        # filepath to the index of data on insideairbnb.com
        self.index_path = os.path.join('cache', 'inside-airbnb-index.bz2')
        self.index = self.load_index()

    def load_index(self):
        try:
            index = pd.read_csv(self.index_path)  # attempt to load from file
        except FileNotFoundError:
            print("Couldn't find the cached index for insideairbnb.com, regenerating it...")
            index = self.regenerate_index()
        return index

    def regenerate_index(self):
        import re
        import requests
        from collections import Counter

        # 148,121 of html as a list of strings
        html = requests.get('http://insideairbnb.com/get-the-data.html').text.splitlines()

        def unique(repeats):
            # Returns only unique items. Preserves the original order.
            return list(Counter(repeats))

        def regextract(pattern):
            matches = [re.search(pattern, line) for line in html]  # non-matches are included as None
            matches = [match.group(1) for match in matches if match]  # the if filters out the None's
            return unique(matches)  # retains only unique matches. Preserves the original order

        def get_dates(place_url):
            place_url = f'http://data.insideairbnb.com/{place_url}/([\d\-]+)/'
            dates = regextract(pattern=place_url)
            return unique(dates)

        # Construct the index dataframe
        index = pd.DataFrame({
            'place_name': regextract(pattern='<h2>(.+)</h2>'),
            'place_url': regextract(pattern='insideairbnb.com/(.+)/[\d\-]+/data/listings')})
        index['dates'] = index['place_url'].apply(get_dates)

        # save index to a compressed form (to 14% the original size)
        # BZ2 compression performed better than ZIP, GZ and XZ in my trial
        index.to_csv(self.index_path)
        return index


if __name__ == "__main__":
    inside = InsideAirBnB()
    print(inside.index.head())
