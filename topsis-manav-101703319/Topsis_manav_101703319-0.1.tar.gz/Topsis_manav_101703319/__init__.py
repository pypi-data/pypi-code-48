from topsis import Topsis
import numpy as np

def main():
	numerical_data = np.array([[250, 16, 12, 5], [200, 16, 8, 3], [300, 32, 16, 4], [275, 32, 8, 4],[225, 16, 16, 2]], dtype = np.float32)
	weights = np.array([1,1,1,1])#Every feature had got same priority
	impact = np.array(["-", "+", "+", "+"])#We want cost to be decreased and rest of the features to increase
	chosen_model_index = Topsis(weights, numerical_data, impact)
	print("The best performing model out of the given models is ",chosen_model_index + 1, " number")

if __name__ == "__main__":
	main()