import os
import json
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error as mse
from xgboost import XGBRegressor

from inside_airbnb import InsideAirBnB

class PredictPrice:
    def __init__(self):
        self.airbnb = InsideAirBnB()

    def get_data(self, location=None):
        # listing_file = ['data/listings.csv.gz']
        # latest_date = self.airbnb.lookup('dates', for_=location)[0]
        # data = self.airbnb.get_data(location_name=location, date=latest_date, data_files=listing_file)
        # listings = data['listings-dat']


        listings = pd.read_csv('listings.gz')
        # listings.to_csv('listings.gz')
        return listings

    def to_Xy(self, listings):
        # Column work

        # Prep the target
        numeric_price = listings['price'].apply(lambda x: float(x.replace('$', '').replace(',', '')))
        listings['log_price'] = numeric_price.apply(lambda x: np.log(x) if x > 0 else 0)
        listings.drop(columns=['price'])

        numeric = listings.select_dtypes(include=np.number)  # a dataframe with just the numeric columns (40 columns)
        strings = listings.select_dtypes(include='O')  # a dataframe with just the string columns (34 columns)

        # Row work
        # originally 36905 rows
        available = listings['availability_365'] > 0  # 21617
        active = pd.to_datetime(listings['last_review']) > pd.to_datetime('2020-02-01')  # 13735
        good_rows = available & active  # 11161

        # Final bundling
        X = numeric[good_rows].drop(columns=['log_price'])
        y = numeric[good_rows]['log_price']
        return X, y

    def baseline(y_train, y_test):
        y_baseline = np.full(y_test.shape, y_train.median())
        return mse(y_test, y_baseline)

    def make_model(self, listings):
        X_train, X_test, y_train, y_test = train_test_split(
            *self.to_Xy(listings),
            test_size=0.2,
            shuffle=True,
            random_state=42,
        )
        self.model = XGBRegressor(n_estimators=1000, objective='reg:squarederror', n_jobs=-1)
        # https://xgboost.readthedocs.io/en/latest/parameter.html

        self.model.fit(X_train, y_train)


    def predict(self, listing):
        pred = self.model.predict(listing)
        return np.exp(pred[0])  # the model actually predicts log price, so np.exp() un-logs it

    def save_model(self):
        cache_folder, model_filename = 'cache', 'model.json'
        model_path = os.path.join(cache_folder, model_filename)
        self.model.save_model(fname=model_path)

    def load_model(self):
        cache_folder, model_filename = 'cache', 'model.json'
        model_path = os.path.join(cache_folder, model_filename)
        self.model = XGBRegressor()
        self.model.load_model(fname=model_path)

    def form_to_listing(self, form_json):
        form_dict = json.loads(form_json)

        for key, value in form_dict.items():
            form_dict[key] = [value]
        listing = pd.DataFrame.from_dict(form_dict)
        return listing

    def predict_price(self, form_json=None):
        form_dict = json.loads(form_json)
        location = form_dict.pop('location')
        listings = self.get_data(location=location)
        self.make_model(listings)

        listing = self.form_to_listing(form_json=form_dict)
        price = self.predict(listing)[0]
        return price

    # TODO: Make a model which can generalize across locations, and then save it to a file in the repo.
if __name__ == "__main__":
    pricer = PredictPrice()
    location_name = pricer.airbnb.lookup(column='name', for_='Paris')
    form_dict = {'location': location_name, 'accommodates': 6, "latitude": 48.849, "longitude": 2.337}
    form_json = json.dumps(form_dict)
    price_estimate = pricer.predict_price(form_json=form_json)
    print(price_estimate)