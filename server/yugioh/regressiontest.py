import json
import zipfile
import pandas as pd
import datetime
import operator

from pandas.io.json import json_normalize

from keras.models import Sequential
from keras.layers import Activation
from keras.layers import BatchNormalization
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import RNN
from keras.layers import LSTM
from keras import regularizers

# from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier

scaler = preprocessing.MinMaxScaler()


def initialize_rnn_network():
    pass


def initialize_ff_network():
    model = Sequential()
    
    # Feed Forward
    model.add(Dense(100, input_dim=59, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(50, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(50, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(50, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(1, activation="sigmoid"))
    model.compile(optimizer='rmsprop',
              loss='binary_crossentropy',
              metrics=['accuracy'])
    
    return model


def train_network(X, y):
    model = initialize_ff_network()
    model.fit(X, y, epochs=10, batch_size=512)
    model.save_weights("model_network_ff_3.h5", overwrite=True)
    return model


def predict_network(model, X, y):
    score = model.evaluate(X, y, batch_size=512)
    print "Score"
    print score

    prediction = model.predict(X[0:12])
    print prediction
    return model


if __name__ == '__main__':
    with zipfile.ZipFile("./small_training_data.json.zip", "r") as z:
        with z.open('small_training_data.json') as f:
            data = json.load(f)
            dfx = json_normalize(data)
            dfy = pd.read_csv('small_training_results.csv', sep=',')
            print dfx.head()
            X = scaler.fit_transform(dfx)
            y = dfy.values[:,1]
            clf1 = LogisticRegression(random_state=0, C=2.0, solver='sag').fit(X, y)
            #clf2 = svm.SVC(C=35, probability=True)
            clf2 = RandomForestClassifier(n_estimators=500, min_samples_split=5, max_depth=30)
            print "Training clf1"
            clf1.fit(X, y)
            print "Training clf2"
            clf2.fit(X, y)
            clf_list = [clf1, clf2]
            print "Training Network"
            network_ff = train_network(X, y)

    with zipfile.ZipFile("./small_test.json.zip", "r") as z:
        with z.open('small_test.json') as f:
            data = json.load(f)
            dfx = json_normalize(data)
            dfy = pd.read_csv('small_test.csv', sep=',')
            X = scaler.fit_transform(dfx)
            y = dfy.values[:,1]
            for clf in clf_list:
                print "Predict"
                print clf.predict(X[:12, :])
                print "Predict Probability"
                print clf.predict_proba(X[:12, :]) 
                print "Score"
                print clf.score(X, y)
            predict_network(network_ff, X, y)



'''
    print clf.coef_
    coeff = {}
    for i in range(0, 59):
        coeff[list(dfx)[i]] = clf.coef_[:, i][0]
    sorted_coeff = sorted(coeff.items(), key=operator.itemgetter(1))
    for c in sorted_coeff:
        print c
'''

'''
print datetime.datetime.now()
df = pd.read_json('small_training_data.json', orient='columns')
print len(df)

for i in range(0, len(X)):
    state = X[i:i+1,:]
    result = y[i]
    prediction = clf.predict(state)[0]
    if prediction == result:
        correct += 1
    total += 1
test_grade = correct / float(total)

X, y = load_iris(return_X_y=True)
clf = LogisticRegression(random_state=0, solver='lbfgs', multi_class='multinomial').fit(X, y)
print "Predict", str(X[:2, :])
print clf.predict(X[:2, :])
print "Predict Probability", str(X[:2, :])
print clf.predict_proba(X[:2, :]) 
print "Score"
print clf.score(X, y)
'''

