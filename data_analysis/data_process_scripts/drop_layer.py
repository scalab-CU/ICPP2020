from keras import backend as K
from keras.engine.topology import Layer
import numpy as np
import tensorflow as tf
import keras
from keras import activations


class random_drop(Layer):

    def __init__(self, ref_len, **kwargs):
        self.ref_points = ref_points
        super(random_drop, self).__init__(**kwargs)


    def call(self, x):
        self.reconstruction = reconstruction
        x_out = x[:, :self.ref_len, :]

        for i in range(len(x)):
            x_len = x[i][0][0]
            idx = random.sample(range(1, x_len+1),self.ref_len )
            idx.sort()
            x_out[i] = x[i, idx, :]

        return x_out

    def compute_output_shape(self, input_shape):
        return (input_shape[0], self.ref_len, input_shape[2])


