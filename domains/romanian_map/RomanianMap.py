from typing import List, Any
from core.problem import SearchProblem

# Classical AIMA Romanian Map Distances
ROMANIA_MAP = {
    'Arad': {'Zerind': 75, 'Sibiu': 140, 'Timisoara': 118},
    'Bucharest': {'Urziceni': 85, 'Pitesti': 101, 'Giurgiu': 90, 'Fagaras': 211},
    'Craiova': {'Drobeta': 120, 'Rimnicu': 146, 'Pitesti': 138},
    'Drobeta': {'Mehadia': 75, 'Craiova': 120},
    'Eforie': {'Hirsova': 86},
    'Fagaras': {'Sibiu': 99, 'Bucharest': 211},
    'Hirsova': {'Urziceni': 98, 'Eforie': 86},
    'Iasi': {'Vaslui': 92, 'Neamt': 87},
    'Lugoj': {'Timisoara': 111, 'Mehadia': 70},
    'Oradea': {'Zerind': 71, 'Sibiu': 151},
    'Pitesti': {'Rimnicu': 97, 'Craiova': 138, 'Bucharest': 101},
    'Rimnicu': {'Sibiu': 80, 'Craiova': 146, 'Pitesti': 97},
    'Urziceni': {'Vaslui': 142, 'Bucharest': 85, 'Hirsova': 98},
    'Zerind': {'Arad': 75, 'Oradea': 71},
    'Sibiu': {'Arad': 140, 'Fagaras': 99, 'Oradea': 151, 'Rimnicu': 80},
    'Timisoara': {'Arad': 118, 'Lugoj': 111},
    'Giurgiu': {'Bucharest': 90},
    'Mehadia': {'Lugoj': 70, 'Drobeta': 75},
    'Vaslui': {'Iasi': 92, 'Urziceni': 142},
    'Neamt': {'Iasi': 87}
}

# Straight Line Distances to Bucharest (for A* Heuristic)
SLD_TO_BUCHAREST = {
    'Arad': 366,
    'Bucharest': 0,
    'Craiova': 160,
    'Drobeta': 242,
    'Eforie': 161,
    'Fagaras': 176,
    'Hirsova': 151,
    'Iasi': 226,
    'Lugoj': 244,
    'Oradea': 380,
    'Pitesti': 100,
    'Rimnicu': 193,
    'Sibiu': 253,
    'Timisoara': 329,
    'Urziceni': 80,
    'Vaslui': 199,
    'Zerind': 374,
    'Giurgiu': 77,
    'Mehadia': 241,
    'Neamt': 234
}

class RomanianMapProblem(SearchProblem):
    """
    The classic routing problem from Artificial Intelligence: A Modern Approach.
    """
    def __init__(self, start: str = 'Arad', goal: str = 'Bucharest'):
        super().__init__(start, goal)

    def get_actions(self, state: str) -> List[str]:
        if state in ROMANIA_MAP:
            return list(ROMANIA_MAP[state].keys())
        return []

    def get_result(self, state: str, action: str) -> str:
        return action

    def get_cost(self, state: str, action: str, next_state: str) -> float:
        if action is not None and state in ROMANIA_MAP and action in ROMANIA_MAP[state]:
            return float(ROMANIA_MAP[state][action])
        if state in ROMANIA_MAP and next_state in ROMANIA_MAP[state]:
            return float(ROMANIA_MAP[state][next_state])
        return 1.0

    def heuristic(self, state: str) -> float:
        """
        Admissible heuristic: Straight Line Distance to the goal.
        NOTE: This predefined heuristic only works if the goal is Bucharest.
        If the goal is changed, we fallback to 0 (making A* behave like Uniform Cost Search).
        """
        if self.goal == 'Bucharest':
            return float(SLD_TO_BUCHAREST.get(state, 0.0))
        return 0.0
