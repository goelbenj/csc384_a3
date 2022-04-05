"""
An AI player for Othello. 
"""

import random
import sys
import time
import math

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
		print(*args, file=sys.stderr, **kwargs)
		
# Method to compute utility value of terminal state
def compute_utility(board, color):
		black, white = get_score(board) # black = 1, white = 2
		if (color == 1):
				return black - white
		elif (color == 2):
				return white - black

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    return 0 #change this!

def opp_color(color):
  return 2 if color == 1 else 1

min_dict = dict()
max_dict = dict()

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0): #returns lowest possibly utility
    # Note: the MAX player is defined by color, and the MIN player is the player we are finding a move for
    if caching:
        if (board, color) in min_dict: return min_dict[(board, color)]

    value = math.inf
    best_move = None
    opp_color = 2 if color == 1 else 1
    moves = get_possible_moves(board, opp_color)
    
    if moves == [] or limit == 0:
        result = (best_move, compute_utility(board, color))
        if caching:
            min_dict[(board, color)] = result
        return result

    for move in moves:
        next_board = play_move(board, opp_color, *move)
        utility = minimax_max_node(next_board, color, limit-1, caching)[1]
        if utility < value:
          best_move = move
          value = utility

    if caching:
        min_dict[(board, color)] = (best_move, value)

    return (best_move, value)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
		# Note: the MIN player is defined by color, and the MAX player is the player we are finding a move for
    if caching:
        if (board, color) in max_dict: return max_dict[(board, color)]

    value = -math.inf
    best_move = None
    moves = get_possible_moves(board, color)
    
    if moves == [] or limit == 0:
        result = (best_move, compute_utility(board, color))
        if caching:
            max_dict[(board, color)] = result
        return result

    for move in moves:
        next_board = play_move(board, color, *move)
        utility = minimax_min_node(next_board, color, limit-1, caching)[1]
        if utility > value:
          best_move = move
          value = utility

    if caching:
      max_dict[(board, color)] = (best_move, value)

    return (best_move, value)

def select_move_minimax(board, color, limit, caching = 0):
    """
		Given a board and a player color, decide on a move. 
		The return value is a tuple of integers (i,j), where
		i is the column and j is the row on the board.  

		Note that other parameters are accepted by this function:
		If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
		Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
		value (see compute_utility)
		If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
		If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
		"""
    return minimax_max_node(board, color, limit, caching)[0] # assume player 1 is MAX player

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching:
        if (board, color) in min_dict: return min_dict[(board, color)]

    value = math.inf
    best_move = None
    opp_color = 2 if color == 1 else 1
    moves = get_possible_moves(board, opp_color)
    
    if moves == [] or limit == 0:
        result = (best_move, compute_utility(board, color))
        if caching:
            min_dict[(board, color)] = result
        return result

    for move in moves:
        next_board = play_move(board, opp_color, *move)
        utility = alphabeta_max_node(next_board, color, alpha, beta, limit-1, caching, ordering)[1]
        if utility < value:
          best_move = move
          value = utility
        beta = min(beta, value)
        if beta <= alpha: return best_move, value

    if caching:
        min_dict[(board, color)] = (best_move, value)

    return (best_move, value)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching:
        if (board, color) in max_dict: return max_dict[(board, color)]

    value = -math.inf
    best_move = None
    moves = get_possible_moves(board, color)
    
    if moves == [] or limit == 0:
        result = (best_move, compute_utility(board, color))
        if caching:
            max_dict[(board, color)] = result
        return result

    for move in moves:
        next_board = play_move(board, color, *move)
        utility = alphabeta_min_node(next_board, color, alpha, beta, limit-1, caching, ordering)[1]
        if utility > value:
          best_move = move
          value = utility
        alpha = max(alpha, value)
        if alpha >= beta: return best_move, value

    if caching:
      max_dict[(board, color)] = (best_move, value)

    return (best_move, value)

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
		Given a board and a player color, decide on a move. 
		The return value is a tuple of integers (i,j), where
		i is the column and j is the row on the board.  

		Note that other parameters are accepted by this function:
		If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
		Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
		value (see compute_utility)
		If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
		If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
		If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
		If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
		"""
    # initialize alpha to -inf, beta to inf
    return alphabeta_max_node(board, color, -math.inf, math.inf, limit, caching, ordering)[0]

####################################################
def run_ai():
		"""
		This function establishes communication with the game manager.
		It first introduces itself and receives its color.
		Then it repeatedly receives the current score and current board state
		until the game is over.
		"""
		print("Othello AI") # First line is the name of this AI
		arguments = input().split(",")
		
		color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light. 
		limit = int(arguments[1]) #Depth limit
		minimax = int(arguments[2]) #Minimax or alpha beta
		caching = int(arguments[3]) #Caching 
		ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

		if (minimax == 1): eprint("Running MINIMAX")
		else: eprint("Running ALPHA-BETA")

		if (caching == 1): eprint("State Caching is ON")
		else: eprint("State Caching is OFF")

		if (ordering == 1): eprint("Node Ordering is ON")
		else: eprint("Node Ordering is OFF")

		if (limit == -1): eprint("Depth Limit is OFF")
		else: eprint("Depth Limit is ", limit)

		if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

		while True: # This is the main loop
				# Read in the current game status, for example:
				# "SCORE 2 2" or "FINAL 33 31" if the game is over.
				# The first number is the score for player 1 (dark), the second for player 2 (light)
				next_input = input()
				status, dark_score_s, light_score_s = next_input.strip().split()
				dark_score = int(dark_score_s)
				light_score = int(light_score_s)

				if status == "FINAL": # Game is over.
						print
				else:
						board = eval(input()) # Read in the input and turn it into a Python
																	# object. The format is a list of rows. The
																	# squares in each row are represented by
																	# 0 : empty square
																	# 1 : dark disk (player 1)
																	# 2 : light disk (player 2)

						# Select the move and send it to the manager
						if (minimax == 1): #run this if the minimax flag is given
								movei, movej = select_move_minimax(board, color, limit, caching)
						else: #else run alphabeta
								movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)
						
						print("{} {}".format(movei, movej))

if __name__ == "__main__":
		run_ai()
