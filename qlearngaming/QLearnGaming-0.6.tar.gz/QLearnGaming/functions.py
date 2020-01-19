import gym
from keras.models import Sequential
import random
from keras.layers import Dense, Flatten, Conv2D
import warnings
warnings.simplefilter("ignore")
from collections import deque
import numpy as np

# THINK ABOUT WHAT ALL GAMES ARE SIMILAR


# IF YOU GUESSED PIXELS YOU ARE CORRECT

# LETS MAKE A DENSE NETWORK FOR THIS
def create_model(environment):

    """
    Create a Sample Model to train or record_events with

    :param environment: Gym Environment
    :return: Keras model 
    >>> model(gym.make('CartPole-v1'))
    <keras.engine.sequential.Sequential object at "">
    """
    try:
        model = Sequential()
        model.add(Dense(45, input_shape=(2,) + environment.observation_space.shape, init='uniform', activation='relu'))
        model.add(Flatten())
        model.add(Dense(30, init='uniform', activation='relu'))
        model.add(Dense(25, init='uniform', activation='relu'))
        model.add(Dense(environment.action_space.n, init='uniform', activation='linear'))
        model.compile(optimizer='adam', loss='mse', metrics=['acc'])
    except:
        raise TypeError("Environment Not Defined Properly")
    return model
# RECORD THE TRAINING RESULTS
def record_events(environment,model,epsilon=0.8,observetime=500):
    """
    Record_events generate a Deque to train on

    :param observetime: Time to run the sample steps
    :param epslion: Changes the chance of a random action
    :param environment: Gym Environment
    :return: D: deque of the sample actions
    :return: State: Numpy Stack of State after game has ended
    
    >> record_events(environment,model)
    array([[[-0.09451254, -0.19551851,  0.01969967,  0.11035413],
        [-0.08670309, -0.39047236,  0.01171324,  0.39932122]]])...

    """
    Deq = deque()

    # WE NEED TO OBSERVE FIRST TO TRAIN OUR MODEL

    observation = environment.reset()

    obs = np.expand_dims(observation, axis=0)
    # Formatting issues

    # Define the state stack
    state = np.stack((obs, obs), axis=1)
    # game starts
    done = False

    for i in range(observetime):
        # Random Action
        if np.random.rand() <= epsilon:
            # Random Action
            action = np.random.randint(0, environment.action_space.n, )
        # Non random action
        else:
            Q = model.predict(state)
            # Highest Q Value is chosen
            action = np.argmax(Q)
        # new reward
        observation_new, reward, done, info = environment.step(action)
        observation_new = np.expand_dims(observation_new, axis=0)
        state_new = np.append(np.expand_dims(observation_new, axis=0), state[:, :1, :], axis=1)
        Deq.append((state, action, reward, state_new, done))
        state = state_new
        if done:
            # IF the game is done
            environment.reset()
            obs = np.expand_dims(observation, axis=0)
            state = np.stack((obs, obs), axis=1)
    return Deq,state
# Sample moves
def train(Deque,state,model,batch_size=50,gamma=0.85):
# STOCHASTIC GRADIENT DESCENT
    """
    Train the data on a Deque
    :param D: Deque of sample game
    :param model: Keras model
    :param batch_size: the batch size
    :return: Trained Model

    >> train(Deq,env,state,model)
    <keras.engine.sequential.Sequential object at 0x7fcfcc891080>

    """
    minibatch = random.sample(Deque, batch_size)
    inputs_shape = (batch_size,) + state.shape[1:]
    # DEFINE THE TRAINING INPUTS
    inputs = np.zeros(inputs_shape)
    # DEFINE THE TRAINING TARGETS
    targets = np.zeros((batch_size, environment.action_space.n))
    for i in range(0, batch_size):
        state = minibatch[i][0]
        action = minibatch[i][1]
        reward = minibatch[i][2]
        state_new = minibatch[i][3]
        done = minibatch[i][4]
        # INPUT
        inputs[i:i + 1] = np.expand_dims(state, axis=0)
            # NEW TARGET
        targets[i] = model.predict(state)
            # FUTURE REWARD
        Q_sa = model.predict(state_new)
        if done:
            targets[i, action] = reward
        else:
            targets[i, action] = reward + gamma * np.max(Q_sa)
        model.train_on_batch(inputs, targets)
    return model
def test(environment,model,display=False):
    """
    Test your model on the Game Environment

    :param environment: The game environment
    :param model:  The model which will be evaluated
    :param display: Show the game?
    >> test(environment,model)
    Reward 9.0
    
    """
    # START THE GAME
    observation = environment.reset()   
    # OBSERVATION
    obs = np.expand_dims(observation, axis=0)
    # NEW STATE
    state = np.stack((obs, obs), axis=1)
    # GAME
    done = False
    # SEE THE REWARD
    accumulative_reward = 0.0
    while not done:
        if display:
            environment.render()  # If supports Display
        Q = model.predict(state)
        # MAX Q IS THE ACTION
        action = np.argmax(Q)
        # GET THE NEW INFORMATION
        observation, reward, done, info = environment.step(action)
        obs = np.expand_dims(observation, axis=0)
        state = np.append(np.expand_dims(obs, axis=0), state[:, :1, :], axis=1)
        accumulative_reward += reward
    return 'Reward ' + str(accumulative_reward)
def trial(env):
    """
    See the game running in action

    :param environment: Game Environment Gym
    """
    for i_episode in range(20):
        observation = env.reset()
        for t in range(100):
            env.render()
            print(observation)
            action = env.action_space.sample()
            observation, reward, done, info = env.step(action)
            if done:
                print("Episode finished after {} timesteps".format(t+1))
                break
    env.close()
