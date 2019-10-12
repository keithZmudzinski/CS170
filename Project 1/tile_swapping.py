import heapq
import copy
from timeit import default_timer as timer #https://stackoverflow.com/a/25823885



states_hash = {}

goal_state = []
goal_state.append([1,2,3])
goal_state.append([4,5,6])
goal_state.append([7,8,0])

def make_node(key = -1, g_n = -1, h_n = -1, state = -1, parent = -1):
    return [key, g_n, h_n, state, parent]

def at_goal(node):
    return True if node[3] == goal_state else False

def get_key(state):
    triple = ''
    for i, row in enumerate(state):
        for j, value in enumerate(row):
            triple += ''.join([str(i), str(j), str(value)])
    triple = hash(int(triple))
    return triple

def expand(node):
    state = node[3]
    row, col = 0, 0
    to_modify = copy.deepcopy(state)
    expanded_states = []
    expanded_nodes = []
    for i in range(3):
        try:
            row, col = i, state[i].index(0)
            break
        except Exception:
            pass
    if row - 1 >= 0:
        to_modify[row][col], to_modify[row - 1][col] = to_modify[row - 1][col], to_modify[row][col] # Swap with above
        key = get_key(to_modify)
        if key not in states_hash:
            states_hash[key] = 1
            expanded_states.append(copy.deepcopy(to_modify))
        to_modify = copy.deepcopy(state)

    if row + 1 < len(state[0]):
        to_modify[row][col], to_modify[row + 1][col] = to_modify[row + 1][col], to_modify[row][col] # Swap with below
        key = get_key(to_modify)
        if key not in states_hash:
            states_hash[key] = 1
            expanded_states.append(copy.deepcopy(to_modify))
        to_modify = copy.deepcopy(state)

    if col - 1 >= 0:
        to_modify[row][col], to_modify[row][col - 1] = to_modify[row][col - 1], to_modify[row][col] # Swap with left ALLOWING ACCESS AT -1
        key = get_key(to_modify)
        if key not in states_hash:
            states_hash[key] = 1
            expanded_states.append(copy.deepcopy(to_modify))
        to_modify = copy.deepcopy(state)

    if col + 1 < len(state[0]):
        to_modify[row][col], to_modify[row][col + 1] = to_modify[row][col + 1], to_modify[row][col] # Swap with right
        key = get_key(to_modify)
        if key not in states_hash:
           states_hash[key] = 1
           expanded_states.append(copy.deepcopy(to_modify))
        to_modify = copy.deepcopy(state)

    for t_state in expanded_states:
        expanded_nodes.append(make_node(state = t_state))

    return expanded_nodes

def manhattan(state, n):
    total = 0
    for i, row in enumerate(state):
        for j, value in enumerate(row):
            if not(value == 0 or ((i * n) + j + 1 == value)):
                correct_row = int((value - 1) / n)
                correct_index = int((value - 1) % n)
                total += (abs(i - correct_row) + abs(j - correct_index))
    return total

def swapping_tiles(state):
    pass

def general_search(initial_state, heuristic, n):
    max_nodes = -1
    count = 0
    nodes = [make_node(0, 0, heuristic(initial_state, n), initial_state, [-1,-1,-1,-1])]
    heapq.heapify(nodes)
    while(True):
        count += 1
        max_nodes = max(max_nodes, len(nodes))
        if len(nodes) == 0:
            return False
        node = heapq.heappop(nodes)
        if at_goal(node):
            return node
        nodes_to_add = expand(node) # Returns nodes with candidate states
        for to_add in nodes_to_add:
            to_add[4] = node # Set parent node
            to_add[2] = heuristic(to_add[3], n) # Run chosen heuristic on to_add state
            to_add[1] = node[1] + 1 # Add 1 to parent g_n (costs are all 1)
            to_add[0] = to_add[1] + to_add[2] # Combine g_n and h_n to get f_n
            heapq.heappush(nodes, to_add)

start_state = []
start_state.append([1,2,3])
start_state.append([4,5,6])
start_state.append([8,7,0])
start = timer()
node = general_search(start_state, manhattan, 3)
end = timer()
print("Time elapsed: " + str(end - start))
if not(node):
    print("Failed")
else:
    while not(node[3] == -1):
        print(node[3], node[1])
        node = node[4]
