class NQueensSolver:
    def __init__(self, n):
        self.n = n
        self.solutions = []

    def solve(self):
        self.solutions = []
        self._backtrack([])
        return self.solutions

    def _is_valid(self, state, row, col):
        for r, c in enumerate(state):
            if c == col or abs(row - r) == abs(col - c):
                return False
        return True

    def _backtrack(self, state):
        row = len(state)
        if row == self.n:
            self.solutions.append(state[:])
            return
        for col in range(self.n):
            if self._is_valid(state, row, col):
                state.append(col)
                self._backtrack(state)
                state.pop() 