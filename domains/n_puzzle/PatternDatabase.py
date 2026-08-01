import array
import os


def _popcount(x: int) -> int:
    return x.bit_count()


class PatternDatabase:
    """Loads a precomputed binary Pattern Database using permutation-rank lookups."""

    def __init__(self, filename: str, *, verbose: bool = True):
        self.filename = filename
        if verbose:
            print(f"Loading Compact Pattern Database: {filename}...")

        if not os.path.exists(filename):
            raise FileNotFoundError(f"PDB file not found: {filename}")

        with open(filename, "rb") as f:
            num_targets = int.from_bytes(f.read(1), byteorder="big")
            target_bytes = f.read(num_targets)
            self.target_chars_ordered = [hex(b)[2:] for b in target_bytes]
            self.target_index = {c: i for i, c in enumerate(self.target_chars_ordered)}
            self.num_targets = num_targets
            raw_data = f.read()

        self.costs = array.array("b", raw_data)
        # Fast tile-char -> slot lookup (0..15 puzzle indices)
        self._tile_slot = [-1] * 16
        for char, slot in self.target_index.items():
            self._tile_slot[int(char, 16)] = slot

        if verbose:
            print(
                f"Loaded {len(self.costs)} patterns ({len(self.costs) / 1024:.1f} KB) "
                f"for tiles {self.target_chars_ordered}."
            )

    def _get_rank(self, positions: list, n: int) -> int:
        used = 0
        rank = 0
        for i, pos in enumerate(positions):
            mask = (1 << pos) - 1
            less = pos - _popcount(used & mask)
            rank = rank * (n - i) + less
            used |= 1 << pos
        return rank

    def get_cost(self, state: str) -> int:
        n = len(state)
        positions = [0] * self.num_targets
        tile_slot = self._tile_slot
        for idx, char in enumerate(state):
            slot = tile_slot[int(char, 16)]
            if slot >= 0:
                positions[slot] = idx
        return self.costs[self._get_rank(positions, n)]


def combined_pdb_heuristic(state: str, pdbs: list) -> int:
    """Evaluate sum of additive PDB costs in a single pass over the board."""
    n = len(state)
    total = 0
    for pdb in pdbs:
        positions = [0] * pdb.num_targets
        tile_slot = pdb._tile_slot
        for idx, char in enumerate(state):
            slot = tile_slot[int(char, 16)]
            if slot >= 0:
                positions[slot] = idx
        total += pdb.costs[pdb._get_rank(positions, n)]
    return total
