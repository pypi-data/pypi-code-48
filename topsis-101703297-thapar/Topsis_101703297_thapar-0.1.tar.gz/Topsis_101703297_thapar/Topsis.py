import numpy as np
import pandas as pd
import sys
def create_evaluation_matrix(mat):

    mat=mat[:,1:]# m rows n columns m alternatives and n criterias
    #print(mat)
    return mat
    ##create_normalised_matrix(mat)
def create_normalised_matrix(mat,weight):
    #print(mat.shape)
    column_squared_sum=np.zeros(mat.shape[1])# for each of the n features
    for j in range(mat.shape[1]):
        for i in range(mat.shape[0]):
            column_squared_sum[j]+=mat[i][j]*mat[i][j]
        column_squared_sum[j]=np.sqrt(column_squared_sum[j])
        mat[:,j:j+1]=mat[:,j:j+1]/column_squared_sum[j]
    #print(column_squared_sum)
    #print(mat)# this is the perfaprmance matrix
    return weighted_normalised_matrix(mat,weight=np.asarray(weight))
def weighted_normalised_matrix( mat,weight):
    totalweight=np.sum(weight)
    weight=weight/totalweight
    weighted_normalised_mat=weight*mat
    return weighted_normalised_mat
    #calculate_ideal_best_and_ideal_worst(weighted_normalised_mat,is_max_the_most_desired=np.asarray([1,1,0,1]))
    # 1 mean max is ideal best and 0 is min value is the ideal best
def calculate_ideal_best_and_ideal_worst(weighted_normalised_mat,is_max_the_most_desired):
    # print("******************************")
    # print(weighted_normalised_mat)
    # print("******************************")
    ideal_best=np.zeros(weighted_normalised_mat.shape[1])
    ideal_worst = np.zeros(weighted_normalised_mat.shape[1])
    for j in range(weighted_normalised_mat.shape[1]):
        if is_max_the_most_desired[j]==1:
            ideal_best[j]=np.max(weighted_normalised_mat[:,j])
            ideal_worst[j] = np.min(weighted_normalised_mat[:, j])
        else:
            ideal_worst[j] = np.max(weighted_normalised_mat[:, j])
            ideal_best[j] = np.min(weighted_normalised_mat[:, j])
    #print(ideal_best)
    #print(ideal_worst)
    return euclidean_distance_from_ideal_best_and_ideal_worst_for_each_alternative(weighted_normalised_mat,ideal_best,ideal_worst)
def euclidean_distance_from_ideal_best_and_ideal_worst_for_each_alternative(mat, ideal_best,ideal_worst):
    euclidean_distance_from_ideal_best=np.zeros(mat.shape[0])
    euclidean_distance_from_ideal_worst=np.zeros(mat.shape[0])
    for i in range(mat.shape[0]):
        eachrowBest=0
        eachRowWorst=0
        for j in range(mat.shape[1]):
            eachrowBest+=(mat[i][j]-ideal_best[j])**2
            eachRowWorst+= (mat[i][j] - ideal_worst[j])**2
        euclidean_distance_from_ideal_best[i]=np.sqrt(eachrowBest)
        euclidean_distance_from_ideal_worst[i]=np.sqrt(eachRowWorst)
    # print("###################")
    # print(euclidean_distance_from_ideal_worst)
    # print(euclidean_distance_from_ideal_best)
    # print("""""""""""""""""""""'""""")
    return performance_score(mat,euclidean_distance_from_ideal_best,euclidean_distance_from_ideal_worst)
def performance_score(mat,euclidean_best,euclidean_worst):
    performance=np.zeros(mat.shape[0])
    for i in range( mat.shape[0]):
        performance[i]=euclidean_worst[i]/(euclidean_best[i]+euclidean_worst[i])
    # print("$$$$$$$$$$$$$$$$")
    # print(performance)
    # print("$$$$$$$$$$$$$$")
    # l=list(performance)
    # rank=[sorted(l,reverse=True).index(x) for x in l]
    # print("perfrmance_score","rank",sep="       ")
    # for i in range(mat.shape[0]):
    #     print(performance[i],rank[i]+1,sep="        ")
    return performance
if __name__=='__main__':
    try:
        filename=sys.argv[1]
    except:
        print('please provide  3 arguements as filename weight max_is_best ')
        sys.exit(1)
    try:
        weight_input = sys.argv[2]
    except:
        print('please provide  2 more arguement')
        sys.exit(1)
    try:
        is_max_the_best_input = sys.argv[3]
    except:
        print('please provide  1 more  arguement')
        sys.exit(1)
    try:
        df = pd.read_csv(filename)
    except:
        print('Could not read the file given by you')
    #print(df.head())
    mat = df.values
    original_matrix=mat
    try:
     is_max_the_best=list(float(e) for e in is_max_the_best_input.split(','))
    except:
        print('could not correctly parse correctly max_is_best arguement ')
    try:
        weights=list(float(w) for w in weight_input.split(','))
    except:
        print(" could not correctly parse weigths argument")

    mat=create_evaluation_matrix(mat)
    weighted_normalised_mat=create_normalised_matrix(mat,weights)
    performance=calculate_ideal_best_and_ideal_worst(weighted_normalised_mat,np.asarray(is_max_the_best))
    l = list(performance)
    rank = [sorted(l, reverse=True).index(x) for x in l]
    print("perfrmance_score", "rank", sep="       ")
    for i in range(mat.shape[0]):
        print(performance[i],rank[i]+1,sep="        ")

