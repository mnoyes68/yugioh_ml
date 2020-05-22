from tensorflow import Graph, Session
import tensorflow as tf

from keras.models import Sequential, load_model
from keras.layers.core import Dense
from keras.optimizers import sgd

from keras.models import Sequential
from keras.layers import Activation
from keras.layers import BatchNormalization
from keras.layers import Flatten
from keras import regularizers

from sklearn.externals import joblib


def initialize_multithread_newtork(weights):
    thread_graph = Graph()
    with thread_graph.as_default():
        thread_session = Session()
        with thread_session.as_default():
            model = initialize_network(weights)
            graph = tf.get_default_graph()

    return model, graph, thread_session


def initialize_network(weights):
    model = Sequential()
    
    # Feed Forward
    model.add(Dense(100, input_dim=59, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(50, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(1, activation="sigmoid"))
    model.compile(optimizer='rmsprop',
              loss='binary_crossentropy',
              metrics=['accuracy'])
    model.load_weights(weights)

    #graph = tf.get_default_graph()
    
    return model


def create_scaler(scaler_file):
    scaler = joblib.load(scaler_file) 
    return scaler