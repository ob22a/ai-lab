from domains.checkers.Checkers import CheckersState, EMPTY, P1_MAN, P1_KING, P2_MAN, P2_KING

def checkers_evaluation(state: CheckersState, player: int) -> float:
    """
    Advanced Heuristic Evaluation Function for Checkers.
    Scores the board from the perspective of the given player (1 or -1).
    """
    if state.is_terminal():
        return state.get_utility(player)
        
    score = 0.0
    
    for r in range(8):
        for c in range(8):
            piece = state.board[r][c]
            if piece == EMPTY:
                continue
                
            # Determine if this piece belongs to the evaluating player
            is_mine = (player == 1 and piece > 0) or (player == -1 and piece < 0)
            multiplier = 1.0 if is_mine else -1.0
            
            # 1. Material Advantage
            if piece in (P1_KING, P2_KING):
                score += 150.0 * multiplier
            else:
                score += 100.0 * multiplier
                
            # 2. Advancement (Pushing standard pieces forward)
            if piece == P1_MAN:
                score += (r * 5.0) * multiplier
            elif piece == P2_MAN:
                score += ((7 - r) * 5.0) * multiplier
                
            # 3. Center Control (Harder to trap pieces in the center)
            if 2 <= c <= 5:
                score += 2.0 * multiplier
                
            # 4. Back Row Defense (Keep pieces on the back row to prevent opponent kings)
            if piece == P1_MAN and r == 0:
                score += 5.0 * multiplier
            elif piece == P2_MAN and r == 7:
                score += 5.0 * multiplier
                
    return score
