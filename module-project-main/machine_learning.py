from sklearn.neighbors import KNeighborsRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline


def train(df):
    df_copy = df[['latitude', 'longitude', 'review_scores_rating', 'price']]
    X = df_copy.drop(columns='price')
    gamma = []
    for x in df_copy['price']:
        x = x.strip('$')
        x = x.replace(',', '')
        gamma.append(float(x))
    df_copy['price'] = gamma
    y = df_copy['price']
    pipe = make_pipeline(SimpleImputer(), KNeighborsRegressor())
    pipe.fit(X, y)
    return pipe

def get_at_it(location):
    locations = InsideAirBnB()
    omega = locations.get_data(location_name=location, date=None, data_files=['data/listings.csv.gz'])
    kappa = omega['listings-dat']
    return kappa
