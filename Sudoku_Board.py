import sys
import copy
import random
import time

# The Sudoku Board Class is simple board consisting of a 2d array
class Sudoku_Board(object):
    def __init__(self):
        self.board_size = 9
        self.block_size = 3
        self.easy_setting = (self.board_size * self.board_size) / 2
        self.board = [0] * self.board_size
        self.isValidBoard = True
        self.givens = {} # dictionary to hold given spots with coordinate (tuple) as key and (int) 0-9 as value
        self.guesses = {} # similar to givens, except the keys will consist of tuples of possible answers 
        for r in xrange(self.board_size): # prefill the board with zeros
            self.board[r] = [0] * self.board_size

    def set(self, row, col, value):
        self.board[row][col] = value

    def get(self, row, col):
        return self.board[row][col]
    # return a copy of the row in a list
    def get_row(self, row):
        return copy.deepcopy(self.board[row])
    def get_col(self, col):
        return copy.deepcopy([self.board[i][col] for i in range(self.board_size)])
    
    # input: when called by a Sudoku Board (self)
    # output: produce a deep copy, which must be assigned ie: new_board = self.copy()
    def copy(self):
        the_copy = Sudoku_Board()
        the_copy.board = copy.deepcopy(self.board)
        the_copy.givens = copy.deepcopy(self.givens)
        the_copy.guesses = copy.deepcopy(self.guesses)
        return the_copy

    # input: a starting x and y value inside of the board
    # output: list of numbers inside sub_block of size block_size * block_size
    # time complexity: n = block_size, O(n^2)
    def get_sub_block(self, start_x, start_y):
        # normalize start x and start y to be the starting block value
        block_size = self.block_size # block size is width and height of square sub-block of numbers
        start_x = (start_x / block_size) * block_size
        start_y = (start_y / block_size) * block_size
        temp = []
        for row in xrange(block_size):
            for col in xrange(block_size):
                temp.append(self.get(start_x + row, start_y + col))
        return temp
    # input: number of spaces to leave as 0's (int)
    # output: generates a psuedo-random (legal) board with the number of spaces specified missing
    @staticmethod
    def generate_random_board(blank_spaces = None):
        random_board = Sudoku_Board()
        if blank_spaces == None:
            blank_spaces = random_board.easy_setting # default board blank spaces = 1/2 of spaces available
        choices = range(1,random_board.board_size + 1)
        line = []
        # make a randomly ordered line of numbers 1 - 9
        while len(choices) > 0:
            num = random.randint(0,len(choices) - 1)
            line.append(choices.pop(num))

        # permute this list to create a random board that is completely filled out
        random_board.board = random_board.generate_board_using_list(line)
        # verify this is a valid board
        if random_board.valid_board():
            # randomly remove number of blank_space specified by user (or by default about half)
            count = blank_spaces
            while count > 0:
                row = random.randint(0, random_board.board_size - 1)
                col = random.randint(0, random_board.board_size - 1)
                if random_board.get(row,col) != 0:
                    random_board.set(row,col, 0) # make board at (row, col) = 0
                    count -= 1
            # verify board is still valid
            if random_board.valid_board():
                random_board.find_givens()
                return random_board
            else:
                print ">>> Started with a random board, but had problems during removing numbers!!!"
                print random_board
                return generate_random_board(blank_spaces)
        else:
            print ">>> !!! problem generating random board, will try again !!!"
            return generate_random_board(blank_spaces)

    # input: a first line (list) which is the length of the board
    # output: a 2d list (board) with the line permuted to be a valid sudoku board
    def generate_board_using_list(self, first_line):
        assert type(first_line) == list
        assert len(first_line) == self.board_size
        permuted_board = [first_line]
        
        for i in xrange(1, self.board_size): # leave first row alone
            next_line = copy.deepcopy(permuted_board[-1])
            if i % self.block_size == 0: # shift by one if start of a new block
                next_line.append(next_line.pop(0))
            else: # normal permutation of 3 spaces
                for x in xrange(self.block_size):
                    next_line.append(next_line.pop(0))
            permuted_board.append(next_line)
        return permuted_board


    # input: a list of numbers (row, col, or sub_block) and an excluded value
    # output: returns True if a duplicate is found in the list (ignoring duplicates of the excluded value)
    # time complexity: n = size of list, O(n log n) 
    @staticmethod
    def has_duplicate(mylist, excluded_value = 0):
        assert mylist.__class__ == list
        mylist.sort()
        i = 0
        while (i < len(mylist)):
            # check all elements of the list to find matches by sorting
            if mylist[i] != excluded_value and mylist[i] == mylist [i - 1]:
                return True
            i += 1
        return False

    # TODO: this potentially has problems.
    # TODO: check sub_block for duplicates
    # TODO: figure out how you are going to exclude the current selected position.
    def valid_move(self, row, col, value):
        '''When passed a row, col, and value, returns True if the move is valid and there are no
        duplicates of value found in the row and col selected, otherwise if a match to Value is
        found, this function will return False.''' 
        assert (0 <= value <= self.board_size)
        assert (0 <= row < self.board_size)
        assert (0 <= col < self.board_size)
        if value != 0: # 0 symbolizes an empty box
            # check row
            temp_row = self.get_row(row)
            temp_row[col] = value # try the current value at position
            if Sudoku_Board.has_duplicate(temp_row):
                return False
            # check col
            temp_col = self.get_col(col)
            temp_col[row] = value # try the current value at position
            if Sudoku_Board.has_duplicate(temp_col):
                return False
            # check sub_block
            temp_sub_block = self.get_sub_block(row, col)
            pos = (row % self.block_size) * self.block_size + (col % self.block_size)
            #print ">>>> Temp Sub Block: " + str(temp_sub_block)
            #print "  >> From (row,col): " + str((row,col))
            #print "  >> Searching for : " + str(value)
            #print ">>>> Position in sub-block trying to be accessed: " + str(pos) + "\n"
            temp_sub_block[pos] = value # try the current value at position
            if Sudoku_Board.has_duplicate(temp_sub_block):
                return False
        return True # return true if a duplicate is not found or value == 0

    def valid_board(self):
        if self.__class__ != Sudoku_Board:
            return False
        # check rows
        for row in xrange(self.board_size):
            if Sudoku_Board.has_duplicate(self.board[row][:]): # pass list by value
                print "Duplicate found in row: " + str(row)
                print self.board[row]
                return False
        # check cols
        for col in xrange(self.board_size):
            tempcol = []
            for row in xrange(self.board_size): # build a temporary column
                tempcol.append(self.get(row, col))
            if Sudoku_Board.has_duplicate(tempcol):
                print "Duplicate found in col: " + str(col) 
                print tempcol
                return False
        # check sub blocks
        start_vals_x = list(xrange(self.board_size))[::self.block_size]
        start_vals_y = start_vals_x
        for x in start_vals_x:
            for y in start_vals_y:
                if Sudoku_Board.has_duplicate(self.get_sub_block(x,y)):
                    print "\n"
                    print self
                    print "Duplicate found in sub block: [" + str(x) + ", " + str(y) + "]"
                    print "Sub block: " + str(self.get_sub_block(x,y)) + "\n"
                    return False
        # if no duplicate is found, return True
        return True

    # input: a Sudoku Board
    # output: True, if board if valid and contains no spaces (0's), otherwise False
    def is_complete(self):
        assert self.__class__ == Sudoku_Board
        if self.valid_board():
            # check for zeros
            for row in self.board:
                for num in row:
                    if num == 0: return False
            return True
        else:
            return False

   
    # TODO: This find givens will be made obsolete after inputing givens is created.  It is used
    #       currently by solve_board
    def find_givens(self):
        assert self.valid_board() # added to ensure that board is valid before finding givens
        for row in xrange(self.board_size):
            for col in xrange(self.board_size):
                tempval = self.get(row, col)
                if 0 < tempval <= self.board_size: # ignore non-valid numbers
                    self.givens[(row,col)] = tempval

    # TODO: Need to catch when a sub_block has 8 values, to fill in the 9th
    # input: a valid sudoku board
    # output: none, but will mutate self.givens by adding other logical values.
    def find_values(self):
        # At this point, we will assume that self is a valid board
        assert self.valid_board()
        self.find_givens()
        # loop through board and find all possible values for each slot, ignoring given slots
        changes_made = False
        for row in xrange(self.board_size):
            for col in xrange(self.board_size):
                temp_key = (row,col)
                if not self.givens.has_key(temp_key):
                    # if not in givens, see if it is in guesses
                    if not self.guesses.has_key(temp_key):
                        # if not in guesses, add key and find all possible values for that position
                        changes_made = True
                        self.guesses[temp_key] = []
                        # only add values that are valid to the guesses list
                        choices = xrange(1, self.board_size + 1) # possible values to insert
                        self.guesses[temp_key] = [ v for v in choices if self.valid_move(row, col, v) ]
                    else: # if (rol, col) key is found in guesses
                        # verify values work with current board and remove values that are not valid
                        self.guesses[temp_key] = [ v for v in self.guesses[temp_key] if self.valid_move(row, col, v)]
                    num_guesses = len(self.guesses[temp_key])
                    # if there are no possible values
                    if num_guesses < 1:
                        print ">>> No possible values for position: " + str(temp_key)
                        # assume this board is not solveable
                    # if there is only 1 possible value 
                    if num_guesses == 1:
                        changes_made = True # flag to verify that changes have been made to the givens list
                        val = self.guesses.pop(temp_key)[0] # gets val and removes entry TODO: make sure this works
                        print ">>> Adding new value to board: " + str(val) + " at " + str(temp_key)
                        # add tuple (row, col) to self.givens as key and value as value
                        self.givens[temp_key] = val
                        # add value to self.board[row][col] = value
                        self.board[row][col] = val
        if changes_made: # if we successfully added values, see with new givens if we can't add some more
            self.find_values()

    def solve_board(self):
        ''' solve_board sets up the board to be solved, including validating the original board,
            finding the given values, then passing on a copy of the board to recursive helper
            function solve_board_helper.'''
        assert self.__class__ == Sudoku_Board
        print self
        s = time.time()
        if self.valid_board():
            self.find_givens() # finds givens of board
            temp = self.copy() # make a new deep copy of board
            # find logical givens
            temp.find_values()
            # starting making guesses to solve the board
            keys = temp.guesses.keys()
            #keys.sort() # TODO: try messing with this to see if timing improves
            keys = sorted(keys, key=lambda key: len(temp.guesses[key]), reverse = True)
            for key in keys:
                print str(key) + ': ' + str(temp.guesses[key])
            solution = temp.solve_board_helper(keys)
            e = time.time()
            print 'Time to solve board: ' + str(e - s) + ' seconds.'
            if solution is None:
                print '>>> There is no solution for this board'
            return solution
        else:
            print '>>> This is not a valid board:'
            print self
            return None

    # input: assumes that the board's guesses dictionary is already filled out by running find_values()
    # output: a solved board, or None if the board is not solveable
    def solve_board_helper(self, keys):
        assert self.__class__ == Sudoku_Board
        if len(keys) < 1:
            if self.is_complete():
                print '---------------------------------------'
                print '!!! FOUND SOLUTION !!!'
                print self
                return self
            else:
                return None
        else: # assume there are guesses left
            first_key = keys.pop() # grab first of the set of keys
            curr_guesses = copy.deepcopy(self.guesses[first_key])
            temp_row = first_key[0]
            temp_col = first_key[1]
            for guess in curr_guesses:
                if self.valid_move(temp_row, temp_col, guess):
                    # if the option is still a valid choice add it and try it
                    self.set(temp_row, temp_col, guess)
                    self.givens[first_key] = guess
                    possible_solution =  self.solve_board_helper(copy.deepcopy(keys))
                    if not possible_solution is None:
                        return possible_solution
                else:
                    pass # skip adding this guess
            if self.givens.has_key(first_key):
                self.givens.pop(first_key)
                self.set(temp_row, temp_col, 0)

    def clear(self):
        self.givens.clear() # remove all given values
        for row in xrange(self.board_size):
            for col in xrange(self.board_size):
                self.board[row][col] = 0

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __repr__(self):
        result = '    0   1   2   3   4   5   6   7   8\n--|-----------|-----------|-----------|\n'
        for i in xrange(self.board_size):
            line = ''
            for num in self.board[i]:
                if num == 0:
                    line += '    ' # display a blank (only for display purposes)
                else:
                    line += str(num) + '   '
            result += str(i) + '   ' + line + '\n'
            if (i+1) % 3 == 0:
                if i != 8:
                    result += '--|-----------|-----------|-----------|\n'
                else:
                    result += '--|-----------|-----------|-----------|'
            else:
                result += '  |           |           |           |\n'
        return result

# Program runs from here

if __name__ == "__main__":
    print "Running sudoku solver as main.\n"
    TEST = True
   # This is for testing
    if TEST:
        LOOP_COUNT = 10
        test_count = 0
        pass_count = 0
        fail_count = 0
        time_start = time.time()
 
        def test_message(passed_test, message, *args):
            global pass_count
            global fail_count
            global test_count
            test_count += 1
            if passed_test:
                print ">>> PASSED TEST: " + message + "\n"
                pass_count += 1
            else:
                print "!!! FAILED TEST: " + message + " !!!\n"
                print "!!! FAILED TEST: " + message + " !!!\n"
                print "!!! FAILED TEST: " + message + " !!!\n"
                fail_count += 1

        test_result = False
        print "TESTING SUDOKU SOLVER\n"

        print "Testing Baord Creation"
        board1 = Sudoku_Board()
        print board1
                   
        # TEST: board initialized with all values equal to zero.
        test_result = True
        for row in xrange(9):
            if test_result == True:
                for col in xrange(9):
                    if board1.board[row][col] != 0:
                        test_result = False
                        break
        m = "board initialized with all values equal to zero."
        test_message(test_result, m)
        m = "is this a valid board"
        test_result = board1.valid_board()
        test_message(test_result, m)

        # TODO: Potential problem with this test or valid_board() method
        # TEST: Get and Set
        print "Testing Board Validation on Valid Board" 
        nums_list = list(xrange(1,board1.board_size + 1))
        for row in xrange(board1.board_size):
            # this if statement prevents the revolving of duplicates into every 3rd row by offsetting value by 1
            if row != 0 and row % board1.block_size == 0:
                nums_list.insert(0, nums_list.pop()) # increment for the next row
            for col in xrange(board1.board_size):
                board1.board[row][col] = nums_list[col]
            for i in xrange(board1.block_size):
                nums_list.insert(0, nums_list.pop()) # places last value of nums_list in first spot
        print board1

        m = "is this a valid board"
        test_result = board1.valid_board()
        test_message(test_result, m)
         
        m = "get() method"
        test_result = True
        for row in xrange(9):
            for col in xrange(9):
                test_result = (board1.get(row,col) == board1.board[row][col])
                if test_result == False:
                    break
            if test_result == False:
                break
        test_message(test_result, m)

        print "Testing Board Validation on Invalid Board" 
        
        for count in xrange(10):
            # generate random (x,y) coords
            temp_coord_x = random.randint(0,8)
            temp_coord_y = random.randint(0,8)
            temp_val = random.randint(1,9)
            original_val = board1.board[temp_coord_x][temp_coord_y]
            # make sure that the temp_val to replace is not the same as what is already there
            while temp_val == original_val:
                temp_val = random.randint(1,9)
                print "> Generating random int: " + str(temp_val)
                
            print "> Inserting random int '" + str(temp_val) + "'  at: [" + str(temp_coord_x) + ", " + str(temp_coord_y) + "]"
            board1.set(temp_coord_x, temp_coord_y, temp_val)
            print board1

            m = "invalid board check (rows) " + str(count)
            test_result = not board1.valid_board()
            test_message(test_result, m)
 
           
            # return the old value
            board1.set(temp_coord_x, temp_coord_y, original_val)

            if not test_result:
                break # stop the loop if an invalid board failed to trigger valid_board()

        # TEST: get_row, get_col
        print "TESTING: get_row, get col"
        print board1
        for row in xrange(9):
            print "Row " + str(row) + ":"
            print board1.get_row(row)
        m = "check row"

        for col in xrange(9):
            print "Col " + str(col) + ":"
            print board1.get_col(col)
        m = "check col"
        
        # TEST: copy()
        print "TESTING: copy()"
        for count in xrange(LOOP_COUNT):
            board2 = Sudoku_Board.generate_random_board()
            board3 = board2.copy()

            # test that it is actually a new copy
            row = random.randint(0, board3.board_size - 1)
            col = random.randint(0, board3.board_size - 1)
            temp_val = board3.get(row, col)
            temp_replacement = random.randint(1, board3.board_size)
            while (temp_val == temp_replacement):
                temp_replacement = random.randint(1, board3.board_size)
            board3.set(row,col,temp_replacement)
            
            m = "new copy of board is new object " + str(count)
            test_result = board2.get(row,col) != board3.get(row,col)
            test_message(test_result, m)
            
            # return old value
            board3.set(row,col,temp_val)

            # test that new board is exactly the same as old board
            m = "all values of copied board are equal" + str(count)
            test_result = board2 == board3
            test_message(test_result, m)
 

        # flip two values
        for count in xrange(LOOP_COUNT):
            # generate random (x,y) coords
            # since swapping with the right value, I only generate rand ints to 7 (to prevent accessing cols
            #   outside of the range of the board
            temp_coord_x = random.randint(0,7)
            temp_coord_y = random.randint(0,7)
            temp_val_left  = board1.get(temp_coord_x, temp_coord_y)
            temp_val_right = board1.get(temp_coord_x, temp_coord_y + 1)

            # swap values
            board1.set(temp_coord_x, temp_coord_y, temp_val_right)
            board1.set(temp_coord_x, temp_coord_y + 1, temp_val_left)

            print board1

            m = "invalid board check (cols) " + str(count)
            test_result = not board1.valid_board()
            test_message(test_result, m)
 
            # return original values
            board1.set(temp_coord_x, temp_coord_y, temp_val_left)
            board1.set(temp_coord_x, temp_coord_y + 1, temp_val_right)

            if not test_result:
                break # stop the loop if an invalid board failed to trigger valid_board()
        
        # Test: Generate Random Valid Boards
        for x in xrange(LOOP_COUNT):
            board1 = Sudoku_Board.generate_random_board(random.randint(0, board1.board_size * board1.board_size))
            print board1
            m = "generate random board: " + str(x)
            test_result = board1.valid_board()
            test_message(test_result, m)

        # Test: find_givens()
        # loop of tests
        print "Testing find_givens()"

        for x in xrange(LOOP_COUNT):
            board1 = Sudoku_Board.generate_random_board()
            board1.find_givens()
            
            test_result = True
            # test that all non-zero values are placed in givens
            for row in xrange(board1.board_size):
                if not test_result: break
                for col in xrange(board1.board_size):
                    if board1.board[row][col] != 0:
                        has_key = board1.givens.has_key((row,col))
                        matches = board1.board[row][col] == board1.givens[(row,col)]
                        test_result = has_key and matches
                    if not test_result: break
            print board1
            m = "all givens are placed in givens " + str(x)
            test_result = board1.valid_board()
            test_message(test_result, m)

        # TEST: find_values()
        print 'Testing find_values()'
        for x in xrange(LOOP_COUNT):
            board1 = Sudoku_Board.generate_random_board()
            board1.find_givens()
            board1.find_values()
            
            test_result = True
            # test that all non-givens are placed in guesses and the guesses has the correct
            # values for possible moves
            m = 'find_values() ' + str(x)
            for row in xrange(board1.board_size):
                if not test_result: break
                for col in xrange(board1.board_size):
                    if board1.board[row][col] == 0:
                        # if the value is zero, the row col should be in guesses and not in givens
                        in_givens = board1.givens.has_key((row,col))
                        in_guesses = board1.guesses.has_key((row,col))
                        all_valid = True
                        for val in board1.guesses[(row,col)]:
                            all_valid = board1.valid_move(row,col,val)
                            if not all_valid: break
                        test_result = not in_givens and in_guesses and all_valid
                        if not test_result:
                            m += ': '
                            if in_givens or not in_guesses:
                                m += '[new value not properly places] '
                            if not all_valid:
                                m += '[all guesses are not correct]'
                            break
            print board1
            test_result = board1.valid_board()
            test_message(test_result, m)
        
        # TEST: solve_board()
        print 'Testing solve_board()'
        for x in xrange(LOOP_COUNT):
            upper_limit = board1.board_size * board1.board_size - board1.board_size
            board_difficulty = random.randint(board1.easy_setting, upper_limit)
            m = 'solve_board(' + str(board_difficulty) + '): test #' + str(x)
            board1 = Sudoku_Board.generate_random_board(board_difficulty) # higher num is harder
            solution = board1.solve_board()
            
            test_result = solution != None and solution.valid_board()
            test_message(test_result, m)

        # displays test result summary:
        time_end = time.time()
        print "ran a total of " + str(test_count) + " tests."
        print "test runtime: " + str(time_end - time_start) + " seconds"
        print "total tests passed: " + str(pass_count)
        print "total tests failed: " + str(fail_count)
        print "\n"
