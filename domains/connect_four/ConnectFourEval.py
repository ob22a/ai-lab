from domains.connect_four.ConnectFour import ConnectFourState, ROWS, COLS

def evaluate_window(window: list, player: int) -> float:
    """
    Evaluates a window of 4 cells.
    Returns a positive score if it favors the player, negative if it favors the opponent.
    """
    score = 0.0
    opponent = -player
    
    player_count = window.count(player)
    empty_count = window.count(0)
    opp_count = window.count(opponent)
    
    if player_count == 4:
        score += 10000.0
    elif player_count == 3 and empty_count == 1:
        score += 100.0
    elif player_count == 2 and empty_count == 2:
        score += 10.0
        
    if opp_count == 3 and empty_count == 1:
        score -= 100.0 # If opponent has 3 in a row, it's a huge threat!
        
    # We do not evaluate opponent_count == 4 because is_terminal() would have caught the loss,
    # or the recursive max/min value would return -10000.
        
    return score

def connect_four_evaluation(state: ConnectFourState, root_player: int) -> float:
    """
    Evaluation heuristic for Connect Four.
    Scores the board based on center control and analyzing all 69 windows of length 4.
    """
    score = 0.0
    board = state.board
    
    # 1. Center Column Preference
    # Pieces in the center are involved in more potential winning lines
    center_array = [board[r][COLS//2] for r in range(ROWS)]
    center_count = center_array.count(root_player)
    score += center_count * 30.0
    
    # 2. Score Horizontal Windows
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, root_player)
            
    # 3. Score Vertical Windows
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, root_player)
            
    # 4. Score Positive Diagonal Windows
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, root_player)
            
    # 5. Score Negative Diagonal Windows
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, root_player)
            
    return score
