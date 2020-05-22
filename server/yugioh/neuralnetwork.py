import json
import zipfile
import pandas as pd
import datetime
import operator

# from sklearn.datasets import load_iris
from sklearn import preprocessing
from pandas.io.json import json_normalize

from keras.models import Sequential
from keras.layers import Activation
from keras.layers import BatchNormalization
from keras.layers import Dense
from keras.layers import Flatten
from keras import regularizers


if __name__ == '__main__':
    scaler = preprocessing.MinMaxScaler()

    with open('training_data.json') as f:
        data = json.load(f)
        dfx = json_normalize(data)

    dfy = pd.read_csv('training_results.csv', sep=',')
    X = scaler.fit_transform(dfx)
    y = dfy.values[:,1]
    model = Sequential()

    # Feed Forward
    model.add(Dense(100, input_dim=59, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    #model.add(Dense(100, input_shape=(59,), activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(50, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(1, activation="sigmoid"))
    model.compile(optimizer='rmsprop',
              loss='binary_crossentropy',
              metrics=['accuracy'])
    
    # Fit the model
    model.fit(X, y, epochs=10, batch_size=512)
    #model.load_weights("model.h5")

    with open('test_data.json') as f:
        data = json.load(f)
        dfx = json_normalize(data)

    dfy = pd.read_csv('test_results.csv', sep=',')
    X = scaler.fit_transform(dfx)
    y = dfy.values[:,1]
    score = model.evaluate(X, y, batch_size=512)
    print "Score"
    print score

    prediction = model.predict(X[0:10])
    print prediction

    '''
    for i in range(0, 10):
        print X[i]
        print type(X[i])
        prediction = model.predict(X[i])
        print prediction
    '''

    model.save_weights("model.h5", overwrite=True)


