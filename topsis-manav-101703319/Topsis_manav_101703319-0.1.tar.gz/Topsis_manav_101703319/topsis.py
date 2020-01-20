import numpy as np

def Topsis(weights, numerical_data, impact):

	try:
		if(numerical_data.shape[1] != weights.shape[0] or weights.shape != impact.shape or numerical_data.shape[1] != impact.shape[0]):
			raise Exception("Given input is not correct")
	except Exception as e:
		print("Given input is incorrect")
		return

	#Converting weight matrix into percent form
	weights = weights/weights.sum()
	#Making normalized matrix
	for i in range(numerical_data.shape[1]):
		numerical_data[:,i] = (numerical_data[:,i]/np.sqrt((numerical_data[:,i]**2).sum()))

	#Multiplying columns with their specific weights
	numerical_data = numerical_data*(weights.reshape(1,numerical_data.shape[1]))

	ideal_best_values = []
	ideal_worst_values = []

	for i in range(numerical_data.shape[1]):
		if(impact[i] == "+"):
			#It indicates this particular feature value need to be increased
			ideal_best_values.append(numerical_data[:,i].max())
			ideal_worst_values.append(numerical_data[:,i].min())
		elif(impact[i] == "-"):
			#This feature value need to be decreased
			ideal_best_values.append(numerical_data[:,i].min())
			ideal_worst_values.append(numerical_data[:,i].max())

	ideal_best_values = np.array(ideal_best_values, dtype = np.float)
	ideal_worst_values = np.array(ideal_worst_values, dtype = np.float)

	euclDist_ideal_best = np.sqrt(((numerical_data - ideal_best_values)**2).sum(axis = 1))
	euclDist_ideal_worst = np.sqrt(((numerical_data - ideal_worst_values)**2).sum(axis = 1))

	performance_score = euclDist_ideal_worst/(euclDist_ideal_best + euclDist_ideal_worst)
	ranking = np.argsort(performance_score)
	return np.argmax(performance_score)#Returning the index of the row having maximum performance score
