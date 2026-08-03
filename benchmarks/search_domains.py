from search.informed.AStar import AStar
from search.uninformed.BidirectionalSearch import BidirectionalSearch
from domains.romanian_map.RomanianMap import RomanianMapProblem
from domains.word_ladder.WordLadder import WordLadderProblem
from domains.sokoban.Sokoban import SokobanProblem
import os

def test_romanian_map():
    print("=== Romanian Map ===")
    problem = RomanianMapProblem(start='Arad', goal='Bucharest')
    solver = AStar(problem)
    result = solver.run()
    
    path_actions = []
    node = result.solution
    while node and node.parent:
        path_actions.append(node.action)
        node = node.parent
    path_actions.reverse()
    
    print(f"Path to Bucharest: {path_actions}")
    print(f"Nodes expanded: {result.nodes_expanded}")
    print(f"Total Cost: {result.path_cost}\n")

def test_word_ladder():
    print("=== Word Ladder ===")
    try:
        # From 'cold' to 'warm'
        problem = WordLadderProblem(start='cold', goal='warm')
        
        # Word Ladder is massive but unweighted. Bidirectional Search is PERFECT for this!
        solver = BidirectionalSearch(problem)
        result = solver.run()
        
        path_states = []
        node = result.solution
        while node:
            path_states.append(node.state)
            node = node.parent
        path_states.reverse()
        
        print("Path from COLD to WARM:")
        for state in path_states:
            print(f"  -> {state}")
            
        print(f"Nodes expanded: {result.nodes_expanded}\n")
    except Exception as e:
        print(f"Failed: {e}\n")

def test_sokoban():
    print("=== Sokoban ===")
    
    # A simple level
    # '#' = Wall, '.' = Target, '$' = Box, '@' = Player
    level = """
#######
#     #
#  $. #
#  @  #
#######
"""
    problem = SokobanProblem(level)
    solver = AStar(problem)
    result = solver.run()
    
    path_actions = []
    node = result.solution
    while node and node.parent:
        path_actions.append(node.action)
        node = node.parent
    path_actions.reverse()
    
    print(f"Path to solve: {path_actions}")
    print(f"Nodes expanded: {result.nodes_expanded}\n")

def main():
    test_romanian_map()
    test_word_ladder()
    test_sokoban()

if __name__ == "__main__":
    main()
