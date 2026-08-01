import array
import gc
import math
import os
from collections import deque

from domains.n_puzzle.NPuzzle import NPuzzle


class PDBGenerator:
    """Generates Compact Binary Additive Pattern Databases for N-Puzzle using 0-1 BFS."""

    def __init__(self, puzzle: NPuzzle, target_tiles: list[str]):
        self.puzzle = puzzle
        # Keep track of target tiles as integers (excluding blank space for cost calculations)
        self.target_tiles = [int(t, 16) for t in target_tiles if t != "0"]
        self.target_set = set(self.target_tiles)
        
        # CRITICAL FIX: The blank tile (0) must be tracked as part of the permutation signature
        # to prevent state tracking collisions when the blank moves among non-target cells.
        self.tracked_elements = self.target_tiles + [0]
        self.target_index = {tile: i for i, tile in enumerate(self.tracked_elements)}
        
        self.num_targets = len(self.tracked_elements)  # Becomes k + 1
        self.num_positions = puzzle.total_tiles

        # Correct mathematical ceiling: perm(n, k + 1) distinct spatial arrangements
        self.total_arrangements = math.perm(self.num_positions, self.num_targets)

    def _get_rank(self, positions: list) -> int:
        """
        Rank an ORDERED tuple of positions into [0, n!/(n-m)!).
        Uses a bitmask-optimized variation of the Lehmer code.
        """
        n = self.num_positions
        used = 0
        rank = 0
        for i, pos in enumerate(positions):
            mask = (1 << pos) - 1
            less = pos - bin(used & mask).count("1")  # unused cells below pos
            rank = rank * (n - i) + less
            used |= 1 << pos
        return rank

    def _positions_by_tile_order(self, abstract_state: tuple) -> list:
        """Extracts the board coordinates of all tracked tiles including the blank space."""
        positions = [0] * self.num_targets
        for idx, tile in enumerate(abstract_state):
            slot = self.target_index.get(tile)
            if slot is not None:
                positions[slot] = idx
        return positions

    def _get_abstract_state(self, full_state: tuple) -> tuple:
        """Filters the board, turning un-tracked pieces into an identical -1 backdrop."""
        return tuple(
            tile if (tile in self.target_set or tile == 0) else -1
            for tile in full_state
        )

    def _pack(self, abstract_state: tuple) -> int:
        """Pack a state into one int (5 bits/cell) — avoids tuple object allocation overhead."""
        packed = 0
        for tile in abstract_state:
            packed = (packed << 5) | (tile + 1)
        return packed

    def _unpack(self, packed: int) -> tuple:
        """Unpacks 5-bit chunks back into an abstract tile array layout."""
        n = self.num_positions
        state = [0] * n
        for i in range(n - 1, -1, -1):
            state[i] = (packed & 0b11111) - 1
            packed >>= 5
        return tuple(state)

    def generate(self, filename: str):
        print(f"Generating Additive Compact PDB for target tiles: {self.target_tiles} ...")
        print(f"  Algorithm: 0-1 BFS (deque)  |  Table size: {self.total_arrangements:,} entries")

        # Fixed array layout maps cleanly to file output footprint
        pdb_array = array.array("b", [-1] * self.total_arrangements)

        # Seed from the abstract goal state
        start_full_state = tuple(range(self.puzzle.total_tiles))
        start_abstract = self._get_abstract_state(start_full_state)
        start_packed = self._pack(start_abstract)
        start_rank = self._get_rank(self._positions_by_tile_order(start_abstract))
        pdb_array[start_rank] = 0

        # Queue tracking format: (cost, packed_state)
        dq: deque[tuple[int, int]] = deque()  
        dq.appendleft((0, start_packed))

        nodes_expanded = 0

        while dq:
            cost, packed_current = dq.popleft()

            current_abstract = self._unpack(packed_current)
            blank_idx = current_abstract.index(0)

            # Validated stale-entry check
            cur_rank = self._get_rank(self._positions_by_tile_order(current_abstract))
            if pdb_array[cur_rank] != -1 and pdb_array[cur_rank] < cost:
                continue  

            nodes_expanded += 1
            if nodes_expanded % 1_000_000 == 0:
                print(f"  Expanded {nodes_expanded:,} states…")

            for neighbor_idx in self.puzzle.moves_map[blank_idx]:
                moving_tile = current_abstract[neighbor_idx]
                
                # Cost criteria: only increment if the blank slides over one of our target tiles!
                move_cost = 1 if moving_tile in self.target_set else 0
                new_cost = cost + move_cost

                state_list = list(current_abstract)
                state_list[blank_idx], state_list[neighbor_idx] = (
                    state_list[neighbor_idx],
                    state_list[blank_idx],
                )
                new_abstract = tuple(state_list)

                rank = self._get_rank(self._positions_by_tile_order(new_abstract))

                # Relax check: Update index if we discovered an unvisited slot or a strictly cheaper path
                if pdb_array[rank] == -1 or new_cost < pdb_array[rank]:
                    pdb_array[rank] = new_cost
                    packed_new = self._pack(new_abstract)
                    if move_cost == 0:
                        dq.appendleft((new_cost, packed_new))
                    else:
                        dq.append((new_cost, packed_new))

        filled = sum(1 for v in pdb_array if v >= 0)
        print(
            f"\n  PDB Generation Complete!"
            f"\n  States filled:  {filled:,} / {self.total_arrangements:,}"
            f"\n  Table size:     {len(pdb_array) / (1024 * 1024):.2f} MB"
        )

        del dq
        gc.collect()

        if os.path.dirname(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "wb") as f:
            f.write(bytes([self.num_targets]))
            # Write out target tiles as hex values
            f.write(bytes(self.target_tiles))
            pdb_array.tofile(f)

        print(f"Saved compact binary database to {filename}\n")
