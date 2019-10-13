import heapq # https://docs.python.org/3/library/heapq.html
import copy # https://stackoverflow.com/a/2612815

def make_node(f_n = -1, g_n = -1, h_n = -1, state = -1, parent = -1):
    '''Constructor function for array that represents a node in the tree'''
    return [f_n, g_n, h_n, state, parent]

def at_goal(input_state, goal_state):
    '''Checks if given node is equivilant to the goal state'''
    return True if input_state == goal_state else False

def get_key(state):
    '''Creates hash key that is unique for each possible board state'''
    triple = ''
    for i, row in enumerate(state):
        for j, value in enumerate(row):
            triple += ''.join([str(i), str(j), str(value)])
    triple = hash(int(triple))
    return triple

def expand(node, seen_states):
    '''For the input node, returns a list of all possible child nodes,
       excluding repetitions'''
    state = node[3]
    row, col = 0, 0
    to_modify = copy.deepcopy(state) # Preserve input state
    expanded_states = []
    expanded_nodes = []
    for i in range(3): # Get row, col indices of 0 (the blank tile)
        try:
            row, col = i, state[i].index(0)
            break
        except Exception:
            pass
    if row - 1 >= 0: # Swap empty tile with tile above
        to_modify[row][col], to_modify[row - 1][col] = to_modify[row - 1][col], to_modify[row][col]
        key = get_key(to_modify)
        if key not in seen_states: #If not a repeated state, add state to child states and mark as seen, same for all similar statements below
            seen_states[key] = 1
            expanded_states.append(copy.deepcopy(to_modify))
        to_modify = copy.deepcopy(state)

    if row + 1 < len(state[0]):# Swap empty tile with tile below
        to_modify[row][col], to_modify[row + 1][col] = to_modify[row + 1][col], to_modify[row][col]
        key = get_key(to_modify)
        if key not in seen_states:
            seen_states[key] = 1
            expanded_states.append(copy.deepcopy(to_modify))
        to_modify = copy.deepcopy(state)

    if col - 1 >= 0: # Swap empty tile with tile to the left
        to_modify[row][col], to_modify[row][col - 1] = to_modify[row][col - 1], to_modify[row][col]
        key = get_key(to_modify)
        if key not in seen_states:
            seen_states[key] = 1
            expanded_states.append(copy.deepcopy(to_modify))
        to_modify = copy.deepcopy(state)

    if col + 1 < len(state[0]): # Swap empty tile with tile to the right
        to_modify[row][col], to_modify[row][col + 1] = to_modify[row][col + 1], to_modify[row][col]
        key = get_key(to_modify)
        if key not in seen_states:
           seen_states[key] = 1
           expanded_states.append(copy.deepcopy(to_modify))
        to_modify = copy.deepcopy(state)

    for t_state in expanded_states:
        expanded_nodes.append(make_node(state = t_state))

    return expanded_nodes

def manhattan(state, n):
    '''For input nxn state, calculates manhattan heuristic from goal state'''
    total = 0
    for i, row in enumerate(state):
        for j, value in enumerate(row):
            # Value in given index not what it should be and not the blank tile
            if not(value == 0 or ((i * n) + j + 1 == value)):
                correct_row = int((value - 1) / n)
                correct_index = int((value - 1) % n)
                total += (abs(i - correct_row) + abs(j - correct_index)) # Add x, y distances from correct location to get manhattan distance
    return total

def misplaced_tiles(state, n):
    '''For input nxn state, calculates misplaced_tiles heuristic from goal state'''
    total = 0
    for i, row in enumerate(state):
        for j, value in enumerate(row):
            # Value in given index not what it should be and not the blank tile
            if not(value == 0 or ((i * n) + j + 1 == value)):
                total += 1
    return total

def none(state, n):
    '''Always return 0 for heuristic evaluator, allowing breadth-first-search'''
    return 0

def general_search(initial_state, goal_state, heuristic, n, hash_table):
    '''Returns goal_state node, max_nodes, expanded_nodes if success, otherwise False, max_nodes, expanded_nodes'''
    expanded_nodes, max_nodes = 0, -1
    nodes = [make_node(0, 0, heuristic(initial_state, n), initial_state, [-1,-1,-1,-1])]
    heapq.heapify(nodes) # Start min_heap, (acts as the queue)
    while(True):
        max_nodes = max(max_nodes, len(nodes)) # Save max number of nodes the queue
        if len(nodes) == 0: # If queue is empty, couldn't find solution
            return False, max_nodes, expanded_nodes
        node = heapq.heappop(nodes) # Gets node with smallest f_n value
        if at_goal(node[3], goal_state): # If find node with goal state, Success!
            return node, max_nodes, expanded_nodes
        nodes_to_add = expand(node, hash_table) # Returns nodes with candidate states
        expanded_nodes += 1 # Save number of nodes expanded
        for to_add in nodes_to_add:
            to_add[4] = node # Set parent node
            to_add[2] = heuristic(to_add[3], n) # Run chosen heuristic on to_add state
            to_add[1] = node[1] + 1 # Add 1 to parent g_n (costs are all 1)
            to_add[0] = to_add[1] + to_add[2] # Combine g_n and h_n to get f_n
            heapq.heappush(nodes, to_add)

def string_from_list(input):
    output = ''
    for x in input[:-1]:
        output +=  (str(x) + ' ')
    output += (str(input[-1]))
    return output

def print_tree(end_node):
    if end_node[4][3] == -1:
        return
    print_tree(end_node[4])
    print(("The best state to expand with a "
        + "g(n) = " + str(end_node[1])
        + " and h(n) = " + str(end_node[2])
        + " is...\n"
        + "                 " + string_from_list(end_node[3][0]) + '\n'
        + "                 " + string_from_list(end_node[3][1]) + '\n'
        + "                 " + string_from_list(end_node[3][2])
        + "   Expanding this node...\n")
    )

def menu():
    seen_states = {}
    start_state = []
    start_state.append([1,2,3])
    start_state.append([4,0,5])
    start_state.append([7,8,6])

    goal_state = []
    goal_state.append([1,2,3])
    goal_state.append([4,5,6])
    goal_state.append([7,8,0])

    print(('Welcome to Keith Zmudzinski\'s 8-puzzle solver.\n'
        + 'Type "1" to use a default puzzle, or "2" to enter your own puzzle.')
        )

    while(True):
        try:
            choice = int(input())
        except ValueError as e:
            print("You must enter a valid integer.")
        if choice == 1 or choice == 2:
            break
        print("Please enter either 1 or 2.")

    if(choice == 2):
        print("Enter your puzzle, use a zero to represent the blank")
        row1 = input("Enter the first row, use tabs or spaces between numbers: ")
        row2 = input("Enter the second row, use tabs or spaces between numbers: ")
        row3 = input("Enter the third row, use tabs or spaces between numbers: ")
        row1 = row1.split()
        row1 = [int(x) for x in row1]
        row2 = row2.split()
        row2 = [int(x) for x in row2]
        row3 = row3.split()
        row3 = [int(x) for x in row3]
        start_state = []
        start_state.append(row1)
        start_state.append(row2)
        start_state.append(row3)
    else:
        print("\n\nDefault puzzle will be used.")

    print(("\nEnter your choice of algorithm\n"
            + "1. Uniform Cost Search\n"
            + "2. A* with the Misplaced Tile heuristic.\n"
            + "3. A* with the Manhattan distance heuristic.")
        )
    while(True):
        try:
            choice = int(input())
        except ValueError as e:
            print("You must enter a valid integer.")
        if choice == 1 or choice == 2 or choice == 3:
            break
        print("Please enter either 1, 2, or 3.")

    heuristic = manhattan if choice == 3 else misplaced_tiles if choice == 2 else none

    print(("\nExpanding state: " + string_from_list(start_state[0])
        + "\n                 " + string_from_list(start_state[1])
        + "\n                 " + string_from_list(start_state[2]) + "\n")
        )

    end_node, max_nodes, expanded_nodes = general_search(start_state, goal_state, heuristic, 3, seen_states)

    if not(end_node):
        print(("There is no solution for this puzzle.\n"
            + "\nThe search algorithm expanded a total of " + str(expanded_nodes) + " nodes.\n"
            + "The maximum number of nodes in the queue at any one time was " + str(max_nodes) + ".")
            )
    else:
        print_tree(end_node[4])
        print(("\nGoal!!\n"
            + "\nTo solve this problem the search algorithm expanded a total of " + str(expanded_nodes) + " nodes.\n"
            + "The maximum number of nodes in the queue at any one time was " + str(max_nodes) + ".\n")
            + "The depth of the goal node was " + str(end_node[1]) + "."
            )





menu()
