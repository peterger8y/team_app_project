import os
import numpy as np
import pandas as pd

from sklearn.metrics import mean_squared_error as mse
from xgboost import XGBRegressor

from inside_airbnb import InsideAirBnB


class PredictPrice:
    def __init__(self):
        pass

    def predict_price(self, form):
        location = form.pop('location')

        listings = self.get_listings(location)

        X, y, my_listing = self.to_Xy(listings, form)

        model = self.make_model(X, y)

        price = self.predict(model, my_listing)
        return price

    def get_listings(self, location):
        airbnb = InsideAirBnB()
        listing_file = ['data/listings.csv.gz']
        latest_date = airbnb.lookup('dates', for_=location)[0]
        data = airbnb.get_data(location_name=location, date=latest_date, data_files=listing_file)
        listings = data['listings-dat']

        # Can speed up local debugging
        # listings.to_csv('listings.gz')  # save to a file (~20 MB)
        # listings = pd.read_csv('listings.gz')  # load from file instead of downloading every time
        return listings

    def to_Xy(self, listings, form, min_availability=0, active_since='2020-02-01'):
        # Only keep listings which are available and active (30% in New York City)
        available = listings['availability_365'] > min_availability
        active = pd.to_datetime(listings['last_review']) > pd.to_datetime(active_since)
        good_rows = available & active

        # Crop X from listings
        columns = form.keys()
        X = listings.loc[good_rows, columns]

        # Prep the target
        y = listings['price'].apply(lambda x: float(x.replace('$', '').replace(',', '')))
        y = y.apply(lambda x: np.log(x) if x > 0 else 0)
        y = y.loc[good_rows]

        # Format the form dictionary to a DataFrame
        my_listing = pd.DataFrame(form, index=[0])
        return X, y, my_listing

    def make_model(self, X, y):
        model = XGBRegressor(n_estimators=1000, objective='reg:squarederror', n_jobs=-1)
        return model.fit(X, y)

    def predict(self, model, listing):
        pred = model.predict(listing)
        return np.exp(pred[0])  # the model actually predicts log price, so np.exp() un-logs it

    # These methods were useful in the Colab notebook, but aren't currently integrated here
    def baseline(self, y_train, y_test):
        y_baseline = np.full(y_test.shape, y_train.median())
        return mse(y_test, y_baseline)

    def over_base(self, y_train, y_test, y_pred):
        mse_base = self.baseline(y_train, y_test)
        mse_gb = mse(y_test, y_pred)
        improvement = 1 - (mse_gb / mse_base)
        return improvement

    def save_model(self, model):
        cache_folder, model_filename = 'cache', 'model.json'
        model_path = os.path.join(cache_folder, model_filename)
        model.save_model(fname=model_path)

    def load_model(self):
        cache_folder, model_filename = 'cache', 'model.json'
        model_path = os.path.join(cache_folder, model_filename)
        model = XGBRegressor()
        model.load_model(fname=model_path)
        return model

    # TODO: Make a model which can generalize across locations, and then save it to a file in the repo.


if __name__ == "__main__":
    # form_json = '{"location": "Paris, \\u00c3\\u008ele-de-France, France", "accommodates": 6, "latitude": 48.849, "longitude": 2.337}'
    form = {"location": "Paris, \\u00c3\\u008ele-de-France, France", "accommodates": 6, "latitude": 48.849,
            "longitude": 2.337}
    pricer = PredictPrice()
    price_estimate = pricer.predict_price(form)
    print(f'This unit will usually cost ${price_estimate:,.2f}/night.')