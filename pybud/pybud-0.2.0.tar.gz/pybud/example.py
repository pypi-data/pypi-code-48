import time


def sample(a, b):
    """
    Test case 1
    """
    x = 8
    y = 14

    x = a + b
    y = x * 2
    print('Math test: ' + str(y))

    fl = 1.234

    a_string = "this is a string"

    num_list = []

    num_list = [500, 600, 700]

    num_list = [100, 200, 700, 800]

    num_list.remove(200)

    dict_test = dict()

    dict_test["one"] = 2
    dict_test = {"one": 1, "two": 2}

    dict_test = {"one": {"yes": "yes"}, "two": 2}

    dict_test["one"]["yes"] = 0

    friends = ['john', 'pat', 'gary', 'michael']
    for i, name in enumerate(friends):
        print("iteration {iteration} is {name}".format(iteration=i, name=name))


def nested_loop():
    """
        Test case 2
    """
    num_list = [500, 600, 700]
    alpha_list = ['x', 'y', 'z']

    for number in num_list:
        print(number)
        time.sleep(1)
        for letter in alpha_list:
            print(letter)

    time.sleep(3.4)
