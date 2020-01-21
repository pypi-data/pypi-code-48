import keras
import random

from keras.layers import Layer

class Stroke(Layer):

    def __init__(self, previous_layer=None, volatility_ratio=.1):
        super(Stroke, self).__init__()
        self.player = previous_layer
        self.num_outputs = previous_layer.output_shape[-1]
        self.vratio = volatility_ratio

    def call(self, input):
        weights = self.player.get_weights()
        num_weights = len(weights)
        for stricken in range(0, int(num_weights * self.vratio)):
            index = random.randint(0, num_weights)
            weights[index] = random.uniform(-.05, .05)
        self.set_weights(weights)
        return input

    def build(self, input_shape):
        weights = self.player.get_weights()
        self.kernel = weights
        super(Stroke, self).build(input_shape)
