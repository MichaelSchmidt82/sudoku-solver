from itertools import chain, combinations
from copy import copy, deepcopy

def one_element_subset(ss):
    return chain(*map(lambda x: combinations(ss, x), range(1, 2)))


class AnnotatedBoard:
    """
    A sudoku board with unknown cells annotated with possible values (sets).
    """

    def __init__(self, board=None):
        """
        Initialize a board with cells which contain no values, and all
        possiblies.
        """
        if not board:
            self.board = [[set({i for i in range(1, 10)}) for _ in range(9)] for _ in range(9)]
            self.unknowns = 81
        elif isinstance(board, type(self)):
            self.board =[[board.board[r][c] for c in range(9)] for r in range(9)]
            self.unknowns = board.unknowns

    def __repr__(self):
        """Display basic board characteristics for interactive interpreters."""
        k = 81 - self.unknowns
        p = k / 0.81
        v = 'valid' if self.is_valid() else 'invalid'
        return 'AnnotatedBoard(%d known, %0.1f%% complete, ' % (k, p) + v + ')'

    def __str__(self):
        """
        Represent the board as a string for printing.

        :rtype: string.
        """
        s = ''
        for r in range(9):
            for c in range(9):
                if c % 3 == 0 and c != 0:
                    s += '| '
                if isinstance(self.board[r][c], int):
                    s += str(self.board[r][c]) + ' '
                else:
                    s += '. '

            if r % 3 == 2 and r != 8:
                s += '\n------+-------+------\n'
            else:
                s += '\n'
        return s

    def __deepcopy__(self, memo): # memo is a dict of id's to copies
        id_self = id(self)        # memoization avoids unnecesary recursion
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)()
        memo[id_self] = _copy
        _copy.unknowns = self.unknowns
        _copy.board = [[set({}) for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                if isinstance(self.board[r][c], set):
                    _copy.board[r][c] = set(v for v in self.board[r][c])
                else:
                    _copy.board[r][c] = self.board[r][c]

        return _copy

    def from_list_of_lists(self, board):
        """
        WIP WIP WIP.

        WIP WIP WIP.
        """
        self.board = board

        if self.is_valid():
            self.unknown_count()
        else:
            raise

    def from_file(self, filename):
        """
        Populate the board using a file.

        :rtype: None
        """
        with open(filename, 'r') as f:
            for r in range(9):
                row = f.readline()
                for c in range(0, 18, 2):
                    if row[c] != '.':
                        self.board[r][int(c / 2)] = int(row[c])

        if not self.is_valid():
            raise

        self.unknown_count()

    def element(self, row, col):
        """
        Return the value, or set of possible values.

        :rtype: int/set()
        """
        if isinstance(self.board[row][col], set):
            return set(self.board[row][col])

        return self.board[row][col]

    def guess(self, row, col, value):
        """
        Set a cell value without deduction.

        :row:   int     row index
        :col:   int     col index
        :value: int     -1 to reset, otherwise 1-9
        :rtype: bool    True if guess was accepted, False otherwise
        """

        old = self.board[row][col]

        if value == -1:
            self.board[row][col] = set(v for v in range(1, 10))
            return self.is_valid(row, col)
        elif isinstance(self.board[row][col], set):
            self.board[row][col] = value
            if self.is_valid(row, col):
                self.unknowns -= 1
                return True
            else:
                self.board[row][col] = old
                return False
        elif isinstance(self.board[row][col], int):
            self.board[row][col] = value
            if self.is_valid(row, col):
                return True
            self.board[row][col] = old
            return False

    def unknown_count(self):
        """
        Scan and return the number of cells without known values.

        :rtype: int    Number of cells which don't contain values.
        """
        count = 0
        for r in range(9):
            for c in range(9):
                if isinstance(self.board[r][c], set):
                    count += 1

        self.unknowns = count
        return count

    def full_deduce(self):
        """
        Deduce values using row, column, and block methods.

        :rtype: bool    True if board is valid, otherwise False
        """
        return (self.block_deduce() and
                self.row_deduce() and
                self.col_deduce())

    def is_valid(self, row=None, col=None):
        """
        Checks if a board is valid by eliminating possibilities in unknown
        cells.

        :rtype: bool    True if board is valid, otherwise False.
        """
        return (self.block_elimination(row, col) and
                self.row_elimination(row) and
                self.col_elimination(col))

    def row_duplicate(self, row=None):
        """
        Check for duplicates at the row level.  Currently not used.

        :row:   int     (Optional) specified row to check.
        :rtype: bool    True if a duplicate exists, otherwise False.
        """
        if not row:
            for r in range(9):
                s = set({})
                for c in range(9):
                    if isinstance(self.board[r][c], int):
                        if self.board[r][c] in s:
                            return True
                        s.add(self.board[r][c])
        else:
            for c in range(9):
                s = set({})
                if isinstance(self.board[row][c], int):
                    if self.board[row][c] in s:
                        return True
                    s.add(self.board[row][c])
        return False

    def col_duplicate(self, col=None):
        """
        Check for duplicates at the column level.  Currently not used.

        :col:   int     (Optional) specified column to check
        :rtype: bool    True if a duplicate exists, otherwise False.
        """
        if not col:
            for c in range(9):
                s = set({})
                for r in range(9):
                    if isinstance(self.board[r][c], int):
                        if self.board[r][c] in s:
                            return True
                        s.add(self.board[r][c])
        else:
            for r in range(9):
                s = set({})
                if isinstance(self.board[r][col], int):
                    if self.board[r][col] in s:
                        return True
                    s.add(self.board[r][col])
        return False

    def block_duplicate(self, row=None, col=None):
        """
        Check for duplicates at the block level.  Currently not used.

        :row:   int     (Optional) When used with col, will search block.
        :col:   int     (Optional) column of cell.
        :rtype: bool    True if a duplicate exists, otherwise False.
        """
        if row is not None and col is not None:
            row_start = row
            while row_start % 3:
                row_start -= 1

            col_start = col
            while col_start % 3:
                col_start -= 1

            s = set({})

            for r in range(row_start, row_start + 3):
                for c in range(col_start, col_start + 3):
                    if isinstance(self.board[r][c], int):
                        if self.board[r][c] in s:
                            return True
                        s.add(self.board[r][c])

        else:
            for row_start in range(0, 9, 3):
                for col_start in range(0, 9, 3):

                    s = set({})

                    for r in range(row_start, row_start + 3):
                        for c in range(col_start, col_start + 3):
                            if isinstance(self.board[r][c], int):
                                if self.board[r][c] in s:
                                    return True
                                s.add(self.board[r][c])

        return False

    def row_deduce(self):
        """
        Deduce values on cells at the row level.

        :rtype: bool    True if board is valid, otherwise False
        """
        for r in range(9):
            s = set({})
            for c in range(9):
                if isinstance(self.board[r][c], set):
                    s = s.union(self.board[r][c])

            subsets = [set({e}) for e in s]
            for subset in subsets:
                flag = False

                for c in range(9):
                    if isinstance(self.board[r][c], set):
                        if subset.issubset(self.board[r][c]):
                            if not flag:
                                flag = True
                            else:
                                flag = False
                                break
                if flag:
                    for c in range(9):
                        if isinstance(self.board[r][c], set):
                            if subset.issubset(self.board[r][c]):
                                self.board[r][c] = subset.pop()
                                self.unknowns -= 1
                                return self.is_valid(row=r, col=c)
        return True

    def col_deduce(self):
        """
        Deduce values on cells at the column level.

        :rtype: bool    True if board is valid, otherwise False.
        """
        for c in range(9):
            s = set({})
            for r in range(9):
                if isinstance(self.board[r][c], set):
                    s = s.union(self.board[r][c])

            subsets = [set({e}) for e in s]
            for subset in subsets:
                flag = False

                for r in range(9):
                    if isinstance(self.board[r][c], set):
                        if subset.issubset(self.board[r][c]):
                            if not flag:
                                flag = True
                            else:
                                flag = False
                                break
                if flag:
                    for r in range(9):
                        if isinstance(self.board[r][c], set):
                            if subset.issubset(self.board[r][c]):
                                self.board[r][c] = subset.pop()
                                self.unknowns -= 1
                                return self.is_valid(row=r, col=c)
        return True

    def block_deduce(self):
        """
        Deduce values on cells at the block level.

        :rtype: bool    True if board is valid, otherwise False
        """
        for row_start in range(0, 9, 3):
            for col_start in range(0, 9, 3):
                s = set({})
                for r in range(row_start, row_start + 3):
                    for c in range(col_start, col_start + 3):
                        if isinstance(self.board[r][c], set):
                            s = s.union(self.board[r][c])

                subsets = [set({e}) for e in s]
                for subset in subsets:
                    flag = False

                    for r in range(row_start, row_start + 3):
                        for c in range(col_start, col_start + 3):
                            if isinstance(self.board[r][c], set):
                                if subset.issubset(self.board[r][c]):
                                    if not flag:
                                        flag = True
                                    else:
                                        flag = False
                                        break
                        else:
                            continue
                        break

                    if flag:
                        for r in range(row_start, row_start + 3):
                            for c in range(col_start, col_start + 3):
                                if isinstance(self.board[r][c], set):
                                    if subset.issubset(self.board[r][c]):
                                        self.board[r][c] = subset.pop()
                                        self.unknowns -= 1
                                        return self.is_valid(row=r, col=c)
                            else:
                                continue
                            break
        return True

    def row_elimination(self, row=None):
        """
        Eliminate possibilities at the row level.

        :row:   int     (Optional) When supplied, eliminate on just one row.
        :rtype: bool    True if board is valid, otherwise False.
        """
        if row is not None:
            s = set({})
            for c in range(9):
                if isinstance(self.board[row][c], int):
                    s.add(self.board[row][c])

            for c in range(9):
                if isinstance(self.board[row][c], set):
                    self.board[row][c] -= s
                    if not len(self.board[row][c]):
                        return False
        else:
            for r in range(9):
                s = set({})
                for c in range(9):
                    if isinstance(self.board[r][c], int):
                        s.add(self.board[r][c])

                for c in range(9):
                    if isinstance(self.board[r][c], set):
                        self.board[r][c] -= s
                        if not len(self.board[r][c]):
                            return False
        return True

    def col_elimination(self, col=None):
        """
        Eliminate possibilities at the column level.

        :col:   int     (Optional) When supplied, eliminate on just one column.
        :rtype: bool    True if board is valid, otherwise False.
        """
        if col is not None:
            s = set({})
            for r in range(9):
                if isinstance(self.board[r][col], int):
                    s.add(self.board[r][col])

            for r in range(9):
                if isinstance(self.board[r][col], set):
                    self.board[r][col] -= s
                    if not len(self.board[r][col]):
                        return False
        else:
            for c in range(9):
                s = set({})
                for r in range(9):
                    if isinstance(self.board[r][c], int):
                        s.add(self.board[r][c])

                for r in range(9):
                    if isinstance(self.board[r][c], set):
                        self.board[r][c] -= s
                        if not len(self.board[r][c]):
                            return False
        return True

    def block_elimination(self, row=None, col=None):
        """
        Eliminate possibilities at the block level.

        :row:   int     (Optional) will resolve corresponding block
        :col:   int     (Optional) required with :row:

        :rtype: bool    True if board is valid, otherwise False
        """
        if row is not None and col is not None:
            row_start = row
            while row_start % 3:
                row_start -= 1

            col_start = col
            while col_start % 3:
                col_start -= 1

            s = set({})

            for r in range(row_start, row_start + 3):
                for c in range(col_start, col_start + 3):
                    if isinstance(self.board[r][c], int):
                        s.add(self.board[r][c])

            for r in range(row_start, row_start + 3):
                for c in range(col_start, col_start + 3):
                    if isinstance(self.board[r][c], set):
                        self.board[r][c] -= s
                        if not len(self.board[r][c]):
                            return False
        else:
            for row_start in range(0, 9, 3):
                for col_start in range(0, 9, 3):

                    s = set({})

                    for r in range(row_start, row_start + 3):
                        for c in range(col_start, col_start + 3):
                            if isinstance(self.board[r][c], int):
                                s.add(self.board[r][c])

                    for r in range(row_start, row_start + 3):
                        for c in range(col_start, col_start + 3):
                            if isinstance(self.board[r][c], set):
                                self.board[r][c] -= s
                                if not len(self.board[r][c]):
                                    return False
        return True
