from sklearn.externals import joblib

from sklearn import preprocessing

def save_scaler():
    scaler = preprocessing.MinMaxScaler()


def load_scaler():
    scaler = joblib.load('scaler_small.pkl')