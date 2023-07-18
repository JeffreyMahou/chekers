## Imports

import argparse # parsing tool
import numpy as np # library for scientific computations
import matplotlib.pyplot as plt # library for plotting purposes

# class

class Checkers(): # class containing the checkers' game

    def __init__(self):

        self._parse()
        self._load_data()
        self._initialize_board()

    def _parse(self): # parsing function

        parser = argparse.ArgumentParser(description='Parsing')
        parser.add_argument('--name', type=str, help='name of the txt file', required=False) # name of txt file
        parser.add_argument('--draw', type=int, help='boolean int, if 1, the board and pieces are drawn', default=False)

        args = parser.parse_args()
        self._name = args.name
        self._draw = args.draw

    def _load_data(self): # load the txt file

        self.moves = [] # list of all the moves of the game

        with open(self._name) as f:
            for line in f.readlines():
                line = line.replace("\n","") # remove the endlines

                line = line.split(",") # split the coordinates to a list
                line = tuple(map(lambda x:7-int(x), line)) # apply a 7-value function so that the (0,0) is now the top left corner
                                                            # this way, the coordinates are easier to adress in self.board

                self.moves.append(line)

    def _mat_to_coords(self, color): # Calculate all the coordinates of a given color

        coords = np.where(self.board==color) # gives 2 lists : x coordinates and y coordinates
        coords = list(zip(coords[0], coords[1])) # converts to one list of tuples (x,y)

        return coords

    def _list_pieces(self): # Returns a dictionnary of all the black pieces' coordinates and all the white pieces coordinates

        whites = self._mat_to_coords(1)
        blacks = self._mat_to_coords(-1)

        pieces = {-1:blacks, 1:whites}

        return pieces

    def _initialize_board(self): # initialize the board and the list of pieces

        self.board = np.zeros((8, 8), dtype=int) # A zero in the board means there are no pieces

        self.board[5::2,::2] = 1 # A one means there is white piece on the board
        self.board[6, 1::2] = 1

        self.board[:3:2, 1::2] = -1 # A minus one means there is a black piece on the board
        self.board[1, ::2] = -1


        self.pieces = self._list_pieces() # initialize the list of pieces

    def is_legal(self, move, color): # returns a boolean telling if a given move is legal

        step_direction = -color # direction the pieces go : whites go up (down in the matrix) and blacks go down (up in the matrix)

        for coord in move:
            if coord<0 or coord>7: # if any of the coordinate is outside the board, return False
                return False

        x_0, y_0, x_1, y_1 = move

        if y_1 != y_0 + step_direction: # if the piece doesn't go only one line up or down, return False
            return False                # note : this function is not called when there is a piece eaten

        if x_1 not in [x_0-1, x_0+1]: # if the piece doesn't go one step left or right, return False
            return False

        if self.board[y_0, x_0] != color: # if the first coordinate doesn't correspond to a piece of the right color, return False
            return False

        if self.board[y_1, x_1] != 0: # if the second coordinate doesn't correspond to an empty space, return False
            return False

        return True # if none of the conditions above was valid, the move is legal, return True

    def moves_available(self, color): # return True if a move is available and False if not

        impossible_rows = {-1:7, 1:0} # rows where a piece can't move
        step_direction = -color # direction the pieces go

        for y,x in self.pieces[color]:

            if y != impossible_rows[color]: # if a piece is in the last row, it can't move

                if x>0: # if a piece is in the first column, it can't go left
                    up_left = self.board[y+step_direction,x-1] == 0 # checks if there is a hole in the up_left diagonal square

                    if up_left:
                        self.output("incomplete") # if there is a hole, the game is incomplete
                        return True

                if x<7: # if a piece is on the last column, it can't go right
                    up_right = self.board[y+step_direction,x+1] == 0 # checks if there is a hole in the up_right diagonal square

                    if up_right:
                        self.output("incomplete") # if there is a hole, the game is incomplete
                        return True

        return False # if no hole was found for any piece, there is no move available


    def capture(self, coord, color): # function that returns the possible captures for a given piece

        y,x = coord

        step_direction = -color # direction the pieces go
        impossible_rows = {-1:[6,7], 1:[0,1]} # rows where a piece can't eat

        forced_moves = [] # list of forced move (possibly 0, 1 or 2 moves)

        if y not in impossible_rows[color]: # if a piece is on one of the last two rows, it can't eat
            if x>1: # if the piece is on one of the two first columns, it can't eat to the left
                up_left = self.board[y+step_direction,x-1] == -color # checks if there is a piece of the opposite color in the
                                                                        # up_left diagonal square
                hole_up_left = self.board[y+2*step_direction, x-2] == 0 # checks if there is a hole two steps away in the up_left
                                                                        # diagonal

                if up_left and hole_up_left:
                    forced_moves.append((x, y, x-2, y+2*step_direction)) # add this diagonal "capture move"

            if x<6: # if the piece is on one of the two last columns, it can't eat to the right
                up_right = self.board[y+step_direction,x+1] == -color # checks if there is a piece of the opposite color in the
                                                                        # up_right diagonal square
                hole_up_right = self.board[y+2*step_direction, x+2] == 0 # checks if there is a hole two steps away in the up_right
                                                                        # diagonal

                if up_right and hole_up_right:
                    forced_moves.append((x, y, x+2, y+2*step_direction)) # add this diagonal "capture move"

        return forced_moves

    def forced(self, color): # function that lists all the forced moves possible for a given color

        forced_moves = []

        for coord in self.pieces[color]:

            forced_moves.extend(self.capture(coord, color))

        return forced_moves

    def output(self, txt, line=None, move=None): # function that returns the correct output

        if txt == "illegal": # illegal move

            raw_move = tuple(map(lambda x:7-x, move)) # translate the coordinates so that (0,0) is the bottom right corner
            print("line {} illegal move: {},{},{},{}".format(line+1, *raw_move))

        if txt == "incomplete": # incomplete game

            print("incomplete game")

        if txt == "whites": # whites win

            print("first")

        if txt == "blacks": # blacks win

            print("second")

        if txt == "tie": # tie

            print("tie")

    def update_board(self, move): # update the board with a given move

        x_0, y_0, x_1, y_1 = move
        eat = False # boolean that says if the move was a "capture move"

        if np.abs(y_1-y_0)>1 and np.abs(x_1-x_0)>1: # if the move has two steps, it is a "capture move"
            eat = True

        self.board[y_1, x_1] = self.board[y_0, x_0] # the piece goes to the new position
        self.board[y_0, x_0] = 0 # the first position leaves a hole

        if eat:
            self.board[int((y_0+y_1)/2), int((x_0+x_1)/2)] = 0 # delete the piece that was eaten

        self.pieces = self._list_pieces() # update the list of pieces

    def count_winner(self): # counts the number of white and black pieces to declare winner

        nb_whites = np.sum(self.board==1) # number of white pieces
        nb_blacks = np.sum(self.board==-1) # number of black pieces

        if nb_whites > nb_blacks:

            self.output("whites") # whites win

        elif nb_whites < nb_blacks:

            self.output("blacks") # blacks win

        else:

            self.output("tie") # tie

    def draw(self): # function that draws the board and the pieces at a given state

        fig, ax = plt.subplots()
        ax.set_xticks(np.arange(0.5, 8.5)) # draw the board on the half coordinates
        ax.set_yticks(np.arange(0.5, 8.5))
        ax.xaxis.grid()
        ax.yaxis.grid()

        ax.imshow(self.board) # show the pieces
        plt.show()

    def play_game(self): # function that plays each move of the txt file

        color = 1 # tells which player it is the turn to play. Whites are 1, Blacks are -1. Whites go first
        multiple = False # tells if we are in a series of possible multiple captures

        for l,move in enumerate(self.moves):

            if self._draw: # we can draw a simplified version of the board with self._draw
                self.draw()

            forced_moves = self.forced(color) # list of forced moves (captures) for a given position

            if multiple and len(self.capture(coord_multiple, -color))>0: # if we are in a line of multiple captures and there are
                                                                      # possibilities to capture again
                if move not in self.capture(coord_multiple, -color): # if the move is not in those possibilities
                    self.output("illegal", l, move) # the move is illegal
                    break

                color *= -1 # since there is a new capture of the same color, the color stays the same

            elif len(forced_moves)>0: # if there are forced moves (captures)
                if move not in forced_moves: # if the move is not in the forced moves
                    self.output("illegal", l, move) # the move is illegal
                    break
                multiple = True # we enter a possible sequence of multiple moves
                coord_multiple = [move[3], move[2]] # we register the coordinates of the capture for future possible multiple captures

            else: # if there is nojeffus capture possible
                if not self.is_legal(move, color): # if the move is illegal
                    self.output("illegal", l, move)
                    break
                multiple = False # we break the possible multiple move sequence

            color *= -1 # We switch to the other player
            self.update_board(move) # update the board with the given legal move

        if self._draw: # draw the last play
            self.draw()

        if l == len(self.moves)-1: # if we read all the moves without illegal moves
            if not self.moves_available(color): # if there are no more moves available
                self.count_winner() # count the pieces and declare the winner

# Executable

Instance = Checkers()
Instance.play_game()






