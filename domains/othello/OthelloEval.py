from domains.othello.Othello import OthelloState, EMPTY

def othello_evaluation(state: OthelloState, player: int) -> float:
    """
    Advanced Heuristic Evaluation Function for Othello.
    Scores the board based on mobility and positional control rather than raw piece count,
    which is a trap for beginner AI in Othello.
    """
    if state.is_terminal():
        return state.get_utility(player)
        
    score = 0.0
    
    # 1. Corner Control (Corners are permanent and extremely valuable)
    corners = [(0,0), (0,7), (7,0), (7,7)]
    for r, c in corners:
        if state.board[r][c] == player:
            score += 100.0
        elif state.board[r][c] == -player:
            score -= 100.0
            
    # 2. Corner Trap Avoidance
    # Playing next to an empty corner often allows the opponent to take the corner.
    danger_zones = {
        (0,0): [(0,1), (1,0), (1,1)],
        (0,7): [(0,6), (1,7), (1,6)],
        (7,0): [(6,0), (7,1), (6,1)],
        (7,7): [(7,6), (6,7), (6,6)]
    }
    
    for corner, dangers in danger_zones.items():
        if state.board[corner[0]][corner[1]] == EMPTY: # Only dangerous if corner is empty
            for dr, dc in dangers:
                if state.board[dr][dc] == player:
                    score -= 30.0
                elif state.board[dr][dc] == -player:
                    score += 30.0
                    
    # 3. Edge Control (Edges are stable and good for setting up corner captures)
    # Exclude corners and danger zones
    for r in range(2, 6):
        if state.board[r][0] == player: score += 10.0
        elif state.board[r][0] == -player: score -= 10.0
        
        if state.board[r][7] == player: score += 10.0
        elif state.board[r][7] == -player: score -= 10.0
        
    for c in range(2, 6):
        if state.board[0][c] == player: score += 10.0
        elif state.board[0][c] == -player: score -= 10.0
        
        if state.board[7][c] == player: score += 10.0
        elif state.board[7][c] == -player: score -= 10.0

    # 4. Mobility (Having more legal moves than the opponent forces them into bad positions)
    # Note: computing opponent mobility requires simulating their turn, which is expensive.
    # We only compute our own mobility as a slight bonus if it's our turn.
    if state.get_current_player() == player:
        actions = state.get_legal_actions()
        if actions != ["PASS"]:
            score += len(actions) * 2.0
            
    return score
