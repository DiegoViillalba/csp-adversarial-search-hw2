# N-queens problem implementation in Python

# In this implementation, we'll use a column-oriented approach.

# NOTE: Though we cna improve this approach via combinatories theory,
# It was kept simple for the sake of understanding backtracking

N = 50

positions = []


def check_movement(queens, move):
    """
    Check the validity of the movement via:

    1. Not sharing the same row.
    2. Not sharing the same diagonal.

    Expects:
        queens: list containing the row of each queen.
                The column corresponds to the index.
        move: tuple (column, row).
    """

    move_column = move[0]
    move_row = move[1]

    for queen_column in range(len(queens)):
        queen_row = queens[queen_column]

        # Check if they share the same row.
        if move_row == queen_row:
            return False

        # Check if they share the same diagonal.
        row_difference = abs(move_row - queen_row)
        column_difference = abs(move_column - queen_column)

        if row_difference == column_difference:
            return False

    return True


def backtrack(positions):
    queen_column = len(positions)

    # If we placed all the queens, we found a solution.
    if queen_column == N:
        print("Solution:", positions)
        return True

    # Try every row in the current column.
    for queen_row in range(N):
        move = (queen_column, queen_row)

        if check_movement(positions, move):
            # Make the movement.
            positions.append(queen_row)

            # Try to place the next queen.
            solution_found = backtrack(positions)

            if solution_found:
                return True

            # Undo the movement and try another row.
            positions.pop()

    # No row worked for the current column.
    return False


backtrack(positions)