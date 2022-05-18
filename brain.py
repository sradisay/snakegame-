import numpy as np
import scipy.special

class Net:
    def __init__(self, num_input, num_hidden, num_output):
        self.num_input = num_input
        self.num_hidden = num_hidden
        self.num_output = num_output

        self.weight_input_hidden = np.random.uniform(-0.5, 0.5, size=(self.num_hidden, self.num_input))
        self.weight_hidden_output = np.random.uniform(-0.5, 0.5, size=(self.num_output, self.num_hidden))
        self.activation_function = lambda x: scipy.special.expit(x)

    def get_outputs(self, inputs_list):
        inputs = np.array(inputs_list,ndmin=2).T
        hidden_inputs = np.dot(self.weight_input_hidden,inputs)
        hidden_outputs = self.activation_function(hidden_inputs)
        final_inputs = np.dot(self.weight_hidden_output, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)
        return final_outputs

    def get_max_value(self, inputs_list):
        outputs = self.get_outputs(inputs_list)

        return outputs

def tests():
    net = Net(2, 5, 2)
    inputs = [0.2,0.6]
    output = net.get_max_value(inputs)
    print('output',output,sep='\n')
tests()

