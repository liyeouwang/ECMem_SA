import numpy as np
import os
import json


config = {
    'TESTCASE_NAME': 'workload',
    'TESTCASE_NUMS': 5,
    # The servers will be allocated at a X * Y grid.
    # J should always eqaul to X * Y.
    'X': 2,
    'Y': 3,
    'J': 6,

    # The number of vehicles.
    'I': 10,
    
    # The number of service types.
    'K': 5,
    # The time unit limit
    'MAX_TIME': 100,
    'EARLIEST_DEADLINE': 80,

    # The properties of a service.
    'DIFF_LOW': 1,
    'DIFF_HIGH': 3,
    'ABILITY_LEVEL': 2,
    'PROB_LOW': 0.2,
    'PROB_HIGH': 0.8,

    'FRESHNESS_MEAN': 10,
    'FRESHNESS_STD': 1,
    'FRESHNESS_MIN': 30,

    'LINEGER_MEAN': 15,
    'LINGER_STD': 10,

    'MEMORY_MEAN': 20,
    'MEMORY_STD': 5
}
TESTCASE_NAME = config['TESTCASE_NAME']
TESTCASE_NUMS = config['TESTCASE_NUMS']
X = config['X']
Y = config['Y']

I = config['I']
J = config['J']
K = config['K']
MAX_TIME = config['MAX_TIME']


if (not os.path.exists(TESTCASE_NAME)):
    os.mkdir(TESTCASE_NAME)

for testcase_index in range(TESTCASE_NUMS):
    # Initialization
    T = np.zeros((J, K), dtype=int)
    C = np.full((J, K), np.inf, dtype=int)
    Tv = np.full((J, J, K), np.inf, dtype=int)
    D = np.full((I, K), -1, dtype=int)
    F = np.full((I, K), -1, dtype=int)
    R = np.full((I, J, MAX_TIME), 0, dtype=int)
    M = np.zeros((K), dtype=int)
    M_bar = np.full((J), 9999999, dtype=int)

    '''
    --------------------------------------------------------------------
    This part deals with the transmitting time T between servers.
    It is proportional to the distance between two servers, The
    distance is |x1-x2| + |y1-y2|.
    We also randomly define Service_Tv to be the computed result loadings 
    of services. 
    Then the transmitting time is Service_Tv * (|x1-x2| + |y1-y2|).

    TODO:
        1. The distribution of Service_Tv. Right now it is uniform(1, 5).
    '''

    Service_Tv = np.random.randint(1, high=5, size=K)
    for j1 in range(J):
        for j2 in range(J):
            Tv[j1, j2, :] = Service_Tv * (abs(j1 // X - j2 // X) + abs(j1 % X - j2 % X))


    '''
    --------------------------------------------------------------------
    This part define T.
    TODO:
        1. How to randomly decide the value?
    '''
    T = np.random.randint(0, MAX_TIME // 4, size=(J, K))

    '''
    --------------------------------------------------------------------
    This part defines C in an easy way. Each service has a difficulty 
    Service_difficulty = uniform(DIFF_LOW, DIFF_HIGH),and each server
    has an Server_ability = uniform(1, ABILITY_LEVEL) to describe if 
    the server is good at service k.

    TODO:
        1. Uniformly decide the power of servers may not be a good idea.
        2. Right now, we don't have specialized servers that is good at
        specific services.
    '''
    DIFF_LOW = config['DIFF_LOW']
    DIFF_HIGH = config['DIFF_HIGH']
    ABILITY_LEVEL = config['ABILITY_LEVEL']
    Service_difficulty = np.random.randint(DIFF_LOW, high=DIFF_HIGH, size=(1, K))
    Server_ability = np.random.randint(1, high=ABILITY_LEVEL, size=(J, 1))
    C = Server_ability * Service_difficulty
    C_avg = np.mean(C, axis=0) # The average computation time of each service


    '''
    --------------------------------------------------------------------
    This part decides D and F.

    TBD:
    1. The probability of a service: uniform(PROB_LOW, PROB_HIGH)
    2. The distribution of deadline: uniform(0, MAX_TIME)
    3. The distribution of freshness: normal(FRESHNESS_MEAN, FRESHNESS_STD)
    '''
    PROB_LOW = config['PROB_LOW']
    PROB_HIGH = config['PROB_HIGH']
    FRESHNESS_MEAN = config['FRESHNESS_MEAN']
    FRESHNESS_STD = config['FRESHNESS_STD']
    FRESHNESS_MIN = config['FRESHNESS_MIN']
    EARLIEST_DEADLINE = config['EARLIEST_DEADLINE']
    workload = 0
    Service_prob = np.array([(PROB_HIGH - PROB_LOW) * np.random.random() + PROB_LOW for _ in range(K)])
    for k in range(K):
        for i in range(I):
            if (np.random.random() < Service_prob[k]):
                workload += C_avg[k]
                D[i][k] = np.random.randint(EARLIEST_DEADLINE, high=MAX_TIME, dtype=int)

                fresh = int(np.random.normal(FRESHNESS_MEAN,  FRESHNESS_STD) // 1)
                F[i][k] = FRESHNESS_MIN if fresh < FRESHNESS_MIN else fresh



    workload = workload / (J * MAX_TIME)

    '''
    --------------------------------------------------------------------
    This part decides R. The map is circullar, which means that when a
    vehicle exceeds the edge, it will appear at the other side.

    TBD:
    1. The distribution of time that a vehicle is lingering in a server's 
        area: normal(LINEGER_MEAN, LINGER_STD)
    '''
    LINEGER_MEAN = config['LINEGER_MEAN']
    LINGER_STD = config['LINGER_STD']
    for i in range(I):
        t = 0
        initial_pos = np.random.randint(0, high=J, dtype=int)
        pos_x = initial_pos // X
        pos_y = initial_pos % X
        while t < MAX_TIME:
            linger_time = int(np.random.normal(LINEGER_MEAN, LINGER_STD)//1)

            R[i][pos_x * X + pos_y][t:t + linger_time] = 1

            # A vehicle can only move (north, south, east, west).
            random_walk = np.random.randint(0, 4, dtype=int)
            if (random_walk == 0):
                pos_x = pos_x + 1
            elif (random_walk == 1):
                pos_x = pos_x - 1
            elif (random_walk == 2):
                pos_y = pos_y + 1
            elif (random_walk == 3):
                pos_y = pos_y - 1
            pos_x = pos_x // X
            pos_y = pos_x % X
            t += linger_time

        R[i][pos_x * X + pos_y][t:] = 1

    '''
    --------------------------------------------------------------------
    This part decides M.

    TBD:
    1. The distribution of M: normal(MEMORY_MEAN, MEMORY_STD)
    '''
    MEMORY_MEAN = config['MEMORY_MEAN']
    MEMORY_STD = config['MEMORY_STD']
    M = np.array(np.random.normal(MEMORY_MEAN, MEMORY_STD, K) // 1, dtype=int)



# --------------------------------------------
# Generate files
    with open(f'./{TESTCASE_NAME}/{testcase_index}_{workload:5.4f}.in', 'w+') as f:
        f.write(f"{I}\n")
        # J
        f.write(f"{J}\n")
        # K
        f.write(f"{K}\n")
        # T_MAX
        f.write(f"{MAX_TIME}\n")
        # T
        for j in range(J):
            for k in range(K):
                f.write(f"{T[j][k]} ")
            f.write("\n")
        # C
        for j in range(J):
            for k in range(K):
                f.write(f"{C[j][k]} ")
            f.write("\n")
        # Tv
        for j in range(J):
            for jj in range(J):
                for k in range(K):
                    f.write(f"{Tv[j][jj][k]} ")
                f.write("\n")
        # D
        for i in range(I):
            for k in range(K):
                f.write(f"{D[i][k]} ")
            f.write("\n")
        # F
        for i in range(I):
            for k in range(K):
                f.write(f"{F[i][k]} ")
            f.write("\n")
        # R
        for i in range(I):
            for j in range(J):
                for t in range(0, MAX_TIME):
                    f.write(f"{R[i][j][t]} ")
                f.write("\n")
        # M
        for k in range(K):
            f.write(f"{M[k]} ")
        f.write("\n")
        # M_bar
        for j in range(J):
            f.write(f"{M_bar[j]} ")
        f.close()

with open(f'{TESTCASE_NAME}/config.json', 'w+') as file:
    json.dump(config, file)