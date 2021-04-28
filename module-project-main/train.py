from inside_airbnb import InsideAirBnB


class Train:
    def __init__(self):
        self.data = self.get_data()

    def get_data(self):
        airbnb = InsideAirBnB()
        data_files = ['data/listings.csv.gz']
        data = airbnb.get_data(location_name='New York City', date='2021-02-04', data_files=data_files)
        return data


if __name__ == "__main__":
    train = Train()
    print(train.data['listings-dat'].head())