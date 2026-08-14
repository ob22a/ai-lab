import random
import time
from typing import Any
from games.GameState import GameState
from games.GameSolver import GameSolver
from games.MCTSNode import MCTSNode

class MCTSSolver(GameSolver):
    """
    Monte Carlo Tree Search Algorithm.
    Plays randomly to terminal states to estimate the utility of actions.
    """
    def __init__(self, num_simulations: int = 1000, exploration_constant: float = 1.414, time_limit_seconds: float = None):
        super().__init__()
        self.num_simulations = num_simulations
        self.time_limit = time_limit_seconds
        self.exploration_constant = exploration_constant
        
    def get_best_action(self, state: GameState) -> Any:
        self.root_player = state.get_current_player()
        root = MCTSNode(state)
        
        simulations_run = 0
        start_time = time.time()
        
        while True:
            # Check termination condition
            if self.time_limit is not None:
                if time.time() - start_time >= self.time_limit:
                    break
            else:
                if simulations_run >= self.num_simulations:
                    break
                    
            # 1. SELECTION
            node = root
            while node.is_fully_expanded() and not node.is_terminal():
                node = node.get_best_child(self.exploration_constant)
                
            # 2. EXPANSION
            if not node.is_terminal():
                action = random.choice(node.untried_actions)
                node.untried_actions.remove(action)
                child_state = node.state.apply_action(action)
                child_node = MCTSNode(child_state, parent=node, action_taken=action)
                node.children[action] = child_node
                node = child_node
                
            # 3. SIMULATION (Random Playout)
            # In massive stochastic games, playing to a terminal state randomly can take too long.
            # So we apply a depth limit to the simulation, returning the heuristic utility.
            current_state = node.state
            sim_depth = 0
            # Let's cap simulation depth to 50 moves to prevent infinite loops in stochastic games
            while not current_state.is_terminal() and sim_depth < 50:
                actions = current_state.get_legal_actions()
                if not actions:
                    break
                action = random.choice(actions)
                current_state = current_state.apply_action(action)
                sim_depth += 1
                
            # 4. BACKPROPAGATION
            # Normalize utility between 0 and 1 for MCTS wins metric
            # For our Lab, Win=+1000, Loss=-1000, Draw=0
            # For Crazy heuristic, score can be anything, but let's say > 0 is good.
            raw_utility = current_state.get_utility(self.root_player)
            if raw_utility > 0:
                win_score = 1.0
            elif raw_utility < 0:
                win_score = 0.0
            else:
                win_score = 0.5 # Draw
                
            # Propagate up the tree
            temp_node = node
            while temp_node is not None:
                temp_node.visits += 1
                # If the node represents an action taken by our opponent, 
                # a high win_score for us is BAD for them. But UCT assumes 'wins' means
                # 'wins from the perspective of the player making the choice at that node'.
                # To simplify, we just track wins for the root player and reverse it during selection if needed.
                # Actually, standard MCTS tracks wins for the player who just moved to reach this node.
                # Let's track wins for the player whose turn it is at the PARENT node.
                if temp_node.parent is not None:
                    parent_player = temp_node.parent.state.get_current_player()
                    if parent_player == self.root_player:
                        temp_node.wins += win_score
                    else:
                        temp_node.wins += (1.0 - win_score)
                temp_node = temp_node.parent
                
            simulations_run += 1
            
        # The search is complete. Return the child with the MOST VISITS, not highest UCT score.
        # This is because visits represents the most deeply explored (and thus most robust) path.
        if not root.children:
            return random.choice(state.get_legal_actions())
            
        best_action = max(root.children.items(), key=lambda item: item[1].visits)[0]
        self.nodes_expanded = simulations_run
        return best_action


class InformationSetMCTSSolver(MCTSSolver):
    """
    Wraps MCTS to handle hidden information (stochastic games with unobservable states).
    At each simulation, it samples a random determinized universe and runs MCTS on it.
    All simulated universes share the same root node.
    """
    def __init__(self, determinize_func, num_simulations: int = 1000, exploration_constant: float = 1.414):
        super().__init__(num_simulations, exploration_constant)
        self.determinize = determinize_func
        
    def get_best_action(self, true_state: GameState) -> Any:
        self.root_player = true_state.get_current_player()
        
        # We create a dummy root node that doesn't actually store a specific state,
        # but just aggregates statistics for the legal root actions.
        # However, the root actions MUST be identical across all determinizations.
        legal_actions = true_state.get_legal_actions()
        
        # Maps action -> (total_wins, total_visits)
        root_stats = {action: [0.0, 0] for action in legal_actions}
        
        for _ in range(self.num_simulations):
            # 1. Determinize: generate a hypothetical universe
            hypothetical_state = self.determinize(true_state)
            
            # 2. Run a single MCTS iteration starting from this universe
            root = MCTSNode(hypothetical_state)
            
            # SELECTION
            node = root
            while node.is_fully_expanded() and not node.is_terminal():
                node = node.get_best_child(self.exploration_constant)
                
            # EXPANSION
            if not node.is_terminal():
                action = random.choice(node.untried_actions)
                node.untried_actions.remove(action)
                child_state = node.state.apply_action(action)
                child_node = MCTSNode(child_state, parent=node, action_taken=action)
                node.children[action] = child_node
                node = child_node
                
            # SIMULATION
            current_state = node.state
            sim_depth = 0
            while not current_state.is_terminal() and sim_depth < 50:
                actions = current_state.get_legal_actions()
                if not actions:
                    break
                action = random.choice(actions)
                current_state = current_state.apply_action(action)
                sim_depth += 1
                
            # BACKPROPAGATION
            raw_utility = current_state.get_utility(self.root_player)
            if raw_utility > 0:
                win_score = 1.0
            elif raw_utility < 0:
                win_score = 0.0
            else:
                win_score = 0.5
                
            temp_node = node
            # Stop right before the root
            while temp_node.parent is not None:
                temp_node.visits += 1
                parent_player = temp_node.parent.state.get_current_player()
                if parent_player == self.root_player:
                    temp_node.wins += win_score
                else:
                    temp_node.wins += (1.0 - win_score)
                    
                # If we are at depth 1, update the root stats
                if temp_node.parent == root:
                    root_stats[temp_node.action_taken][1] += 1
                    root_stats[temp_node.action_taken][0] += win_score
                    
                temp_node = temp_node.parent
                
        # Return the action with the most visits across all determinized worlds
        best_action = max(root_stats.items(), key=lambda item: item[1][1])[0]
        self.nodes_expanded = self.num_simulations
        return best_action
