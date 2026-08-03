import os
from typing import List, Tuple, Set
from core.problem import SearchProblem

class WordLadderProblem(SearchProblem):
    """
    Finds the shortest path from a start word to a goal word by changing one letter at a time.
    Every intermediate step must be a valid dictionary word.
    """
    def __init__(self, start: str, goal: str, dictionary_path: str = None):
        super().__init__(start.lower(), goal.lower())
        
        if len(self.start) != len(self.goal):
            raise ValueError("Start and goal words must be the same length!")
            
        if dictionary_path is None:
            # Default to the downloaded words.txt in the same directory
            dir_path = os.path.dirname(os.path.realpath(__file__))
            dictionary_path = os.path.join(dir_path, 'words.txt')
            
        self.dictionary: Set[str] = set()
        self._load_dictionary(dictionary_path, len(self.start))

    def _load_dictionary(self, filepath: str, word_length: int):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dictionary file not found at {filepath}")
            
        with open(filepath, 'r') as f:
            for line in f:
                word = line.strip().lower()
                # We only need to store words of the exact length we are playing with!
                if len(word) == word_length:
                    self.dictionary.add(word)
                    
        # Ensure start and goal are in dictionary (or manually add them so it doesn't crash)
        self.dictionary.add(self.start)
        self.dictionary.add(self.goal)

    def get_actions(self, state: str) -> List[str]:
        actions = []
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        
        # Try replacing each letter with every other letter in the alphabet
        for i in range(len(state)):
            for char in alphabet:
                if char != state[i]:
                    new_word = state[:i] + char + state[i+1:]
                    if new_word in self.dictionary:
                        actions.append(new_word)
                        
        return actions

    def get_result(self, state: str, action: str) -> str:
        return action

    def get_cost(self, state: str, action: str, next_state: str) -> float:
        return 1.0

    def heuristic(self, state: str) -> float:
        """
        Admissible Heuristic: Hamming Distance (Number of differing letters).
        Since each action only changes 1 letter, we are guaranteed to need at least
        'hamming_distance' actions to reach the goal.
        """
        diff = 0
        for i in range(len(state)):
            if state[i] != self.goal[i]:
                diff += 1
        return float(diff)
